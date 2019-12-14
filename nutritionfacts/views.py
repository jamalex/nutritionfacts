import datetime
import json
import re

from ipware.ip import get_trusted_ip, get_ip
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Trunc
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .geo import get_ip_info
from .models import (
    Pingback,
    IPLocation,
    Instance,
    ChannelStatistics,
    FacilityStatistics,
    Message,
    StatisticsPingback,
    MessageStatuses,
    BirthYearStats,
    GenderCount,
    GenderStats,
)
from .decorators import json_response
from .utils import load_zipped_json, version_matches_range

# matches with kolibri gender constants
GENDER_MAPPING = {"m": "MALE", "f": "FEMALE", "ns": "NOT_SPECIFIED", "d": "DEFERRED"}


def login_required_ajax(function):
    """
    Just make sure the user is authenticated to access a certain ajax view

    Otherwise return a HttpResponse 401 - authentication required
    instead of the 302 redirect of the original Django decorator
    """

    def _decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                response = view_func(request, *args, **kwargs)
            elif request.method == "OPTIONS":
                response = HttpResponse("", status=200)
            else:
                response = HttpResponse("Unauthorized", status=401)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            return response

        return _wrapped_view

    return _decorator(function)


@csrf_exempt
@require_http_methods(["POST"])
@json_response
def pingback(request):
    try:
        payload = load_zipped_json(request.body)
    except ValueError:
        return HttpResponseBadRequest("Sorry, please send a valid JSON object.")

    saved_at = datetime.datetime.now()

    kolibri_version = payload.get("version") or ""

    # get the client IP address and look up location for it
    ip_address = get_trusted_ip(request) or get_ip(request)
    iplocation, _ = IPLocation.objects.update_or_create(
        ip_address=ip_address, defaults=get_ip_info(ip_address)
    )

    # extract the mode specified in the payload
    mode = payload.get("mode") or ""
    # check whether it's a dev version and mark mode as "dev"
    if not mode and "dev" in kolibri_version:
        mode = "dev"
    # check whether it matches any of the host-based or ip-based mappings
    if not mode:
        mode = iplocation.get_inferred_mode()

    # build an Instance object if we don't already have one, and update timestamps
    instance_id = payload.get("instance_id")
    defaults = {
        "platform": payload.get("platform") or "",
        "python_version": payload.get("sysversion") or "",
        "database_id": payload.get("database_id") or "",
        "node_id": payload.get("node_id") or "",
    }
    instance, created = Instance.objects.get_or_create(
        instance_id=instance_id, defaults=defaults
    )
    if created:
        instance.first_seen = saved_at
    instance.last_seen = saved_at
    instance.last_mode = mode or instance.last_mode
    instance.save()

    # create the Pingback objects itself
    pingback = Pingback.objects.create(
        instance=instance,
        ip=iplocation,
        kolibri_version=kolibri_version,
        installer=payload.get("installer", ""),
        mode=mode,
        language=payload.get("language", ""),
        timezone=payload.get("timezone", ""),
        saved_at=saved_at,
        uptime=payload.get("uptime") or None,
        server_timestamp=payload.get("timestamp") or None,
    )

    # for backwards compatibility purposes, we can't send JSON to pre-0.11 versions of Kolibri, so check here
    if version_matches_range(kolibri_version, "<0.11.0"):
        return HttpResponse("")

    messages = get_relevant_messages(mode=mode, version=kolibri_version)

    return {"id": pingback.id, "messages": messages}


def get_relevant_messages(mode, version):

    allowed_statuses = [MessageStatuses.ACTIVE.name]

    # enable "staged" messages to be shown
    STAGING_PREFIX = "staged-msgs"
    if mode.startswith(STAGING_PREFIX):
        allowed_statuses.append(MessageStatuses.STAGED.name)

    # set the version to a specified value with something like "staged-msgs-ver-0.12.3"
    STAGING_VER_PREFIX = STAGING_PREFIX + "-ver-"
    if mode.startswith(STAGING_VER_PREFIX):
        version = mode[len(STAGING_VER_PREFIX) :]

    # get all messages that are version-based and match the provided version
    message_queryset = (
        Message.objects.filter(status__in=allowed_statuses)
        .exclude(version_range="")
        .values("msg_id", "version_range", "link_url", "i18n", "timestamp")
    )
    messages = [
        msg
        for msg in message_queryset
        if version_matches_range(version, msg["version_range"])
    ]

    # add the old test messages as needed
    if mode.startswith("msg-"):
        messages.append(
            {
                "msg_id": mode,
                "version_range": "",
                "link_url": "https://www.latlmes.com/arts/return-of-the-golden-age-of-comics-1",
                "i18n": {
                    "en": {
                        "link_text": "More information...",
                        "msg": "You are now running with mode '{}'!".format(mode),
                        "title": "Important!",
                    },
                    "es-es": {
                        "link_text": "Más información...",
                        "msg": "¡Ahora estás corriendo con el modo '{}'!".format(mode),
                        "title": "¡Importante!",
                    },
                },
                "timestamp": datetime.date.today(),
            }
        )

    # if showing staging messages for testing, remove version spec from response so it always gets shown
    if mode.startswith(STAGING_PREFIX):
        for message in messages:
            message["version_range"] = "*"

    return messages


def get_and_create_demographic_objects(data, learner=True):
    birth_year_stats = gender_stats = None
    if data:
        bys = data["bys"]
        birth_year_stats = BirthYearStats.objects.create(
            average=bys["a"],
            variance=bys["v"],
            total_specified=bys["ts"],
            deferred_count=bys["d"],
            is_learner=learner,
        )
        gs = data["gs"]
        gender_stats = GenderStats.objects.create(is_learner=learner)
        for key in gs:
            count = gs[key].get("count")
            # only create gender count if we have useful metrics
            if count:
                GenderCount.objects.create(
                    gender=GENDER_MAPPING.get(key, "UNKNOWN"),
                    count=count,
                    genderstats=gender_stats,
                )
    return birth_year_stats, gender_stats


@csrf_exempt
@require_http_methods(["POST"])
@json_response
def statistics(request):

    try:
        payload = load_zipped_json(request.body)
    except ValueError:
        return HttpResponseBadRequest("Sorry, please send a valid JSON object.")

    pingback = Pingback.objects.get(id=payload["pi"])

    statspingback = StatisticsPingback.objects.create(
        pingback=pingback,
        ip_address=get_trusted_ip(request) or get_ip(request),
        saved_at=datetime.datetime.now(),
    )

    channels = payload.get("c", [])
    facilities = payload.get("f", [])

    for channel in channels:
        (
            birth_year_stats_learners,
            gender_stats_learners,
        ) = get_and_create_demographic_objects(channel.get("dsl"), learner=True)
        (
            birth_year_stats_non_learners,
            gender_stats_non_learners,
        ) = get_and_create_demographic_objects(channel.get("dsnl"), learner=False)
        ChannelStatistics.objects.create(
            pingback=pingback,
            statspingback=statspingback,
            channel_id=channel["ci"],
            version=channel.get("v"),
            updated=channel.get("u"),
            popular_ids=channel.get("pi", []),
            popular_counts=channel.get("pc", []),
            storage=channel.get("s"),
            summ_started=channel.get("ss"),
            summ_complete=channel.get("sc"),
            sess_kinds=channel.get("sk", {}),
            sess_user_count=channel.get("suc"),
            sess_anon_count=channel.get("sac"),
            sess_user_time=channel.get("sut"),
            sess_anon_time=channel.get("sat"),
            birth_year_stats_learners=birth_year_stats_learners,
            birth_year_stats_non_learners=birth_year_stats_non_learners,
            gender_stats_learners=gender_stats_learners,
            gender_stats_non_learners=gender_stats_non_learners,
        )

    for facility in facilities:
        (
            birth_year_stats_learners,
            gender_stats_learners,
        ) = get_and_create_demographic_objects(facility.get("dsl"), learner=True)
        (
            birth_year_stats_non_learners,
            gender_stats_non_learners,
        ) = get_and_create_demographic_objects(facility.get("dsnl"), learner=False)
        FacilityStatistics.objects.create(
            pingback=pingback,
            statspingback=statspingback,
            facility_id=facility["fi"],
            settings=facility.get("s", {}),
            learners_count=facility.get("lc"),
            learner_login_count=facility.get("llc"),
            coaches_count=facility.get("cc"),
            coach_login_count=facility.get("clc"),
            first_log=facility.get("f"),
            last_log=facility.get("l"),
            summ_started=facility.get("ss"),
            summ_complete=facility.get("sc"),
            sess_kinds=facility.get("sk", {}),
            lesson_count=facility.get("lec"),
            exam_count=facility.get("ec"),
            exam_log_count=facility.get("elc"),
            att_log_count=facility.get("alc"),
            exam_att_log_count=facility.get("ealc"),
            sess_user_count=facility.get("suc"),
            sess_anon_count=facility.get("sac"),
            sess_user_time=facility.get("sut"),
            sess_anon_time=facility.get("sat"),
            birth_year_stats_learners=birth_year_stats_learners,
            birth_year_stats_non_learners=birth_year_stats_non_learners,
            gender_stats_learners=gender_stats_learners,
            gender_stats_non_learners=gender_stats_non_learners,
        )

    return {"messages": []}


def health_check(request):

    return HttpResponse("OK")


@login_required_ajax
@json_response
def countries(request):

    instances = Instance.objects.all().filter(last_mode="")

    ips = IPLocation.objects.filter(pingbacks__mode="")
    results = ips.values("country_name").annotate(
        count=Count("pingbacks__instance_id", distinct=True)
    )

    countries = {}

    for count, country in reversed(
        sorted([(result["count"], result["country_name"]) for result in results])
    ):
        if country:
            countries[country] = count

    date_from = datetime.datetime.now() - datetime.timedelta(hours=1)
    pingbacks = Pingback.objects.filter(saved_at__gte=date_from).values(
        "ip__latitude", "ip__longitude"
    )
    pingback_locations = [
        {"lat": p["ip__latitude"], "long": p["ip__longitude"]}
        for p in pingbacks
        if p["ip__latitude"]
    ]

    return {
        "country_total": len(countries),
        "instance_total": instances.count(),
        "last_hour_locations": pingback_locations,
        "country_counts": countries,
    }


def get_instance_stats_for_frequency(
    instances, frequency, running_average_weight=0.3, periods=None
):

    frequency_durations = {
        "day": 24 * 60 * 60,
        "week": 24 * 60 * 60 * 7,
        "month": 24 * 60 * 60 * 30.44,
    }

    assert frequency in frequency_durations

    now = timezone.now()

    history = list(
        instances.annotate(start=Trunc("first_seen", frequency))
        .values("start")
        .annotate(count=Count("instance_id"))
        .order_by("start")
    )

    # if requested, only include the last X periods
    if periods:
        history = history[-periods:]

    # check what portion of the latest time period has already elapsed
    latest = history[-1]
    elapsed = (now - latest["start"]).total_seconds() / frequency_durations[frequency]
    if elapsed <= 1:
        # scale up projections according to how much of the period we still have to go
        projected = int(round(latest["count"] / elapsed))
        history.pop()
    else:
        # in this case, we haven't seen anything yet in the current period, so it's all 0
        projected = 0
        latest = {"start": None, "count": 0}

    # calculate running average
    running_average = history[0]["count"]
    for period in history:
        running_average = (period["count"] * running_average_weight) + (
            running_average * (1 - running_average_weight)
        )
        period["start"] = period["start"].date()
        period["running_average"] = int(round(running_average))

    return {
        "history": history,
        "running_average": int(round(running_average)),
        "current_actual": latest["count"],
        "current_projected": projected,
    }


@login_required_ajax
@json_response
def timeline(request):

    instances = Instance.objects.all().filter(last_mode="")

    return {
        "daily": get_instance_stats_for_frequency(instances, "day", periods=21),
        "weekly": get_instance_stats_for_frequency(instances, "week", periods=12),
        "monthly": get_instance_stats_for_frequency(instances, "month"),
    }


@login_required_ajax
@json_response
def versions(request):

    pingbacks = (
        Pingback.objects.filter(mode="")
        .annotate(month=Trunc("saved_at", "month"))
        .values("month", "kolibri_version")
        .annotate(count=Count("instance_id", distinct=True))
        .order_by("month")
    )

    by_month = defaultdict(dict)

    vers = set()

    for p in pingbacks:
        version = re.findall(r"\d+\.\d+\.\d+", p["kolibri_version"])[0]
        vers.add(tuple([int(c) for c in version.split(".")]))
        counts = by_month[str(p["month"].date())]
        counts[version] = counts.get(version, 0) + p["count"]

    versions = [".".join([str(c) for c in ver]) for ver in sorted(vers)]

    by_version = {
        ver: [vals.get(ver, 0) for vals in by_month.values()] for ver in versions
    }

    colors = [ver[1] - 7 for ver in sorted(vers)]

    return {
        "by_month": by_month,
        "by_version": by_version,
        "months": list(by_month.keys()),
        "colors": colors,
    }


@login_required_ajax
@json_response
def migrations(request):

    instances = (
        Instance.objects.filter(last_mode="")
        .annotate(count=Count("pingbacks__ip__country_name", distinct=True))
        .filter(count__gt=1)
    )

    migrations = {}
    for instance in instances:
        mig = list(instance.pingbacks.values_list("ip__latitude", "ip__longitude"))
        migrations[instance.instance_id] = ([mig[0]] if mig[0][0] else []) + [
            mig[i] for i in range(1, len(mig)) if mig[i] != mig[i - 1] and mig[i][0]
        ]

    return migrations


@login_required
def chart(request):
    domain = request.GET.get("domain", "https://telemetry.learningequality.org")
    return TemplateResponse(
        request, "chart.html", {"request": request, "TELEMETRY_DATA_DOMAIN": domain}
    )
