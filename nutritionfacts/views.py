import datetime
import json
from ipware.ip import get_trusted_ip, get_ip

from django.db.models import Count
from django.db.models.functions import Trunc
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .geo import get_ip_info
from .models import Pingback, IPLocation, Instance
from .decorators import json_response


SPECIAL_HOST_MODES = {
    "ucsd.edu": "ucsd",
}


@csrf_exempt
@require_http_methods(["POST"])
def pingback(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return HttpResponseBadRequest("Sorry, please send a valid JSON object.")

    saved_at = datetime.datetime.now()

    kolibri_version = payload.get("version") or ""

    # get the client IP address and look up location for it
    ip_address = get_trusted_ip(request) or get_ip(request)
    iplocation, _ = IPLocation.objects.update_or_create(ip_address=ip_address, defaults=get_ip_info(ip_address))

    # extract the mode specified in the payload
    mode = payload.get("mode") or ""
    # check whether it's a dev version and mark mode as "dev"
    if not mode and "dev" in kolibri_version:
        mode = "dev"
    # check whether it matches any of the host-based mappings
    if not mode:
        for host in SPECIAL_HOST_MODES:
            if host in iplocation.host:
                mode = SPECIAL_HOST_MODES[host]
                break

    # build an Instance object if we don't already have one, and update timestamps
    instance_id = payload.get("instance_id")
    defaults = {
        "platform": payload.get("platform") or "",
        "python_version": payload.get("sysversion") or "",
        "database_id": payload.get("database_id") or "",
        "node_id": payload.get("node_id") or "",
    }
    instance, created = Instance.objects.get_or_create(instance_id=instance_id, defaults=defaults)
    if created:
        instance.first_seen = saved_at
    instance.last_seen = saved_at
    instance.last_mode = mode or instance.last_mode
    instance.save()

    # create the Pingback objects itself
    Pingback.objects.create(
        instance=instance,
        ip=iplocation,
        kolibri_version=kolibri_version,
        mode=mode,
        saved_at=saved_at,
        uptime=payload.get("uptime") or None,
    )

    return HttpResponse("")


def health_check(request):

    return HttpResponse("OK")


@json_response
def countries(request):

    instances = Instance.objects.filter(last_mode="")

    ips = IPLocation.objects.filter(pingbacks__mode="")
    results = ips.values("country_name").annotate(count=Count("pingbacks__instance_id", distinct=True))

    countries = {}

    for count, country in reversed(sorted([(result["count"], result["country_name"]) for result in results])):
        if country:
            countries[country] = count

    return {
        "country_total": len(countries),
        "instance_total": instances.count(),
        "country_counts": countries,
    }


def get_instance_stats_for_frequency(instances, frequency, running_average_weight=0.3):

    frequency_durations = {
        "day": 24 * 60 * 60,
        "week": 24 * 60 * 60 * 7,
        "month": 24 * 60 * 60 * 30.44,
    }

    assert frequency in frequency_durations

    now = timezone.now()

    history = list(
        instances.annotate(start=Trunc('first_seen', frequency))
                 .values('start')
                 .annotate(count=Count('instance_id'))
                 .order_by("start")
    )

    latest = history[-1]
    elapsed = (now - latest["start"]).total_seconds() / frequency_durations[frequency]
    if elapsed <= 1:
        projected = int(round(latest["count"] / elapsed))
        history.pop()
    else:
        projected = 0
        latest = {"start": None, "count": 0}

    running_average = history[0]["count"]
    for period in history:
        running_average = (period["count"] * running_average_weight) + (running_average * (1 - running_average_weight))
        period["start"] = period["start"].date()
        period["running_average"] = int(round(running_average))

    return {
        "history": history,
        "running_average": int(round(running_average)),
        "current_actual": latest["count"],
        "current_projected": projected,
    }


@json_response
def timeline(request):

    instances = Instance.objects.filter(last_mode="")

    return {
        "daily": get_instance_stats_for_frequency(instances, "day"),
        "weekly": get_instance_stats_for_frequency(instances, "week"),
        "monthly": get_instance_stats_for_frequency(instances, "month"),
    }
