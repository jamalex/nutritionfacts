import datetime
import uuid

from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from enum import Enum

from . import mode_mappings


class Pingback(models.Model):
    class Meta:
        verbose_name = "Pingback"

    instance = models.ForeignKey(
        "Instance",
        blank=True,
        null=True,
        related_name="pingbacks",
        on_delete=models.PROTECT,
    )

    ip = models.ForeignKey(
        "IPLocation",
        blank=True,
        null=True,
        related_name="pingbacks",
        on_delete=models.PROTECT,
    )

    # What Kolibri version is this ping from
    kolibri_version = models.CharField(max_length=50)

    # What installer type was used to install Kolibri
    installer = models.CharField(max_length=80, blank=True)

    # The "mode" the Kolibri instance is running in (e.g. "source", "demo", "production")
    mode = models.CharField(max_length=30, blank=True)

    # The language value under device settings
    language = models.CharField(max_length=15, blank=True)

    # The timezone the server is set to
    timezone = models.CharField(max_length=40, blank=True)

    # The date this ping was received
    saved_at = models.DateTimeField()

    # How long the server has been running (in minutes)
    uptime = models.IntegerField(blank=True, null=True)

    # The date on the sending device when this ping was sent (to check offsets)
    server_timestamp = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{instance} from {ip} at {saved_at:%Y-%m-%d %H:%M}".format(
            instance=(self.instance_id or "?")[:6],
            ip=self.ip_id,
            saved_at=self.saved_at,
        )

    def set_mode_from_ip_if_needed(self):
        if self.mode:
            return
        mode = self.ip.get_inferred_mode()
        if not mode:
            return
        self.mode = mode
        self.save()
        print("set mode on pingback {} to {}".format(self.id, mode))
        instance = self.instance
        if not instance.last_mode:
            instance.last_mode = mode
            instance.save()
            print("set mode on instance {} to {}".format(instance.instance_id, mode))


class Instance(models.Model):
    class Meta:
        verbose_name = "Instance"

    # The unique identifier for this Kolibri instance
    instance_id = models.CharField(max_length=32, primary_key=True)

    # The operating system this Kolibri instance is running on
    platform = models.CharField(max_length=200, blank=True)

    # The python version running this Kolibri instance
    python_version = models.CharField(max_length=300, blank=True)

    # The database-specific id of the Kolibri instance
    database_id = models.CharField(max_length=32, blank=True)

    # The unique device identifier based on the MAC address
    node_id = models.CharField(max_length=32, blank=True)

    first_seen = models.DateTimeField(blank=True, null=True)

    last_seen = models.DateTimeField(blank=True, null=True)

    last_mode = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return "{instance}, on {platform}, with Python {python}".format(
            instance=(self.instance_id or "?")[:6],
            platform=self.platform,
            python=self.python_version.split()[0],
        )


class IPLocation(models.Model):
    class Meta:
        verbose_name = "IP Location"

    # IPv6 addresses can be as long as 45 characters
    ip_address = models.CharField(max_length=45, primary_key=True)

    city = models.CharField(max_length=100, blank=True)
    subdivision = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    continent_code = models.CharField(max_length=10, blank=True)
    continent_name = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    accuracy_radius = models.IntegerField(blank=True, null=True)
    postal_code = models.CharField(max_length=30, blank=True)
    time_zone = models.CharField(max_length=50, blank=True)
    host = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return "{ip} in {city}, {country}".format(
            ip=self.ip_address, city=self.city or "?", country=self.country_name or "?"
        )

    def get_inferred_mode(self):
        mode = ""
        for host in mode_mappings.SPECIAL_HOST_MODES:
            if host in self.host:
                mode = mode_mappings.SPECIAL_HOST_MODES[host]
                break
        for ip_prefix in mode_mappings.SPECIAL_IP_MODES:
            if self.ip_address.startswith(ip_prefix):
                mode = mode_mappings.SPECIAL_IP_MODES[ip_prefix]
                break
        return mode


class StatisticsPingback(models.Model):
    # extra metadata to support debugging of
    # https://sentry.io/organizations/learningequality/issues/858657624/
    ip_address = models.CharField(max_length=45)
    saved_at = models.DateTimeField(blank=True)
    pingback = models.ForeignKey(Pingback, on_delete=models.PROTECT)


class BirthYearStats(models.Model):
    average = models.FloatField(blank=True, null=True)
    standard_deviation = models.FloatField(blank=True, null=True)
    total_specified = models.IntegerField(blank=True, null=True)
    deferred_count = models.IntegerField(blank=True, null=True)
    not_specified_count = models.IntegerField(blank=True, null=True)


class GenderStats(models.Model):
    gender_counts = JSONField(default=dict)


class ChannelStatistics(models.Model):

    pingback = models.ForeignKey(Pingback, on_delete=models.PROTECT)

    statspingback = models.ForeignKey(
        StatisticsPingback, on_delete=models.PROTECT, blank=True, null=True
    )

    # top-level info about channel
    channel_id = models.CharField(max_length=10)
    version = models.IntegerField(blank=True, null=True)
    updated = models.DateField(blank=True, null=True)

    # content_id's and view counts of most popular content from this channel
    popular_ids = ArrayField(models.CharField(max_length=10), default=list)
    popular_counts = ArrayField(models.IntegerField(), default=list)

    # storage used by channel, in MB
    storage = models.IntegerField(blank=True, null=True)

    # aggregate info about content summary logs
    summ_started = models.IntegerField(blank=True, null=True)
    summ_complete = models.IntegerField(blank=True, null=True)
    sess_kinds = JSONField(default=dict)

    # aggregate info about content session logs
    sess_user_count = models.IntegerField(blank=True, null=True)
    sess_anon_count = models.IntegerField(blank=True, null=True)
    sess_user_time = models.IntegerField(blank=True, null=True)
    sess_anon_time = models.IntegerField(blank=True, null=True)

    # demographic info (added in 0.13)
    birth_year_stats_learners = models.ForeignKey(
        BirthYearStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="channel_birthyearstats_learner",
    )
    birth_year_stats_non_learners = models.ForeignKey(
        BirthYearStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="channel_birthyearstats_nonlearner",
    )
    gender_stats_learners = models.ForeignKey(
        GenderStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="channel_genderstats_learner",
    )
    gender_stats_non_learners = models.ForeignKey(
        GenderStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="channel_genderstats_nonlearner",
    )

    # added in 0.14
    sess_anon_count_no_visitor_id = models.IntegerField(blank=True, null=True)
    users_with_logs = models.IntegerField(blank=True, null=True)
    anon_visitors_with_logs = models.IntegerField(blank=True, null=True)


class FacilityStatistics(models.Model):

    pingback = models.ForeignKey(Pingback, on_delete=models.PROTECT)

    statspingback = models.ForeignKey(
        StatisticsPingback, on_delete=models.PROTECT, blank=True, null=True
    )

    facility_id = models.CharField(max_length=10)

    settings = JSONField(default=dict)

    # info about users by kind (how many, and how long spent logged in)
    learners_count = models.IntegerField(blank=True, null=True)
    learner_login_count = models.IntegerField(blank=True, null=True)
    coaches_count = models.IntegerField(blank=True, null=True)
    coach_login_count = models.IntegerField(blank=True, null=True)

    # dates for the first and last logs for the facility
    first_log = models.DateField(blank=True, null=True)
    last_log = models.DateField(blank=True, null=True)

    # aggregate info about content summary logs
    summ_started = models.IntegerField(blank=True, null=True)
    summ_complete = models.IntegerField(blank=True, null=True)
    sess_kinds = JSONField(default=dict)

    # info about exams and lessons and attempts
    lesson_count = models.IntegerField(blank=True, null=True)
    exam_count = models.IntegerField(blank=True, null=True)
    exam_log_count = models.IntegerField(blank=True, null=True)
    att_log_count = models.IntegerField(blank=True, null=True)
    exam_att_log_count = models.IntegerField(blank=True, null=True)

    # aggregate info about content session logs
    sess_user_count = models.IntegerField(blank=True, null=True)
    sess_anon_count = models.IntegerField(blank=True, null=True)
    sess_user_time = models.IntegerField(blank=True, null=True)
    sess_anon_time = models.IntegerField(blank=True, null=True)

    # demographic info (added in 0.13)
    birth_year_stats_learners = models.ForeignKey(
        BirthYearStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="facility_birthyearstats_learner",
    )
    birth_year_stats_non_learners = models.ForeignKey(
        BirthYearStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="facility_birthyearstats_nonlearner",
    )
    gender_stats_learners = models.ForeignKey(
        GenderStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="facility_genderstats_learner",
    )
    gender_stats_non_learners = models.ForeignKey(
        GenderStats,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="facility_genderstats_nonlearner",
    )

    # added in 0.14
    class_count = models.IntegerField(blank=True, null=True)
    group_count = models.IntegerField(blank=True, null=True)
    sess_anon_count_no_visitor_id = models.IntegerField(blank=True, null=True)
    users_with_logs = models.IntegerField(blank=True, null=True)
    anon_visitors_with_logs = models.IntegerField(blank=True, null=True)


class MessageStatuses(Enum):
    DISABLED = "Disabled"
    STAGED = "Staged"
    ACTIVE = "Active"


class Message(models.Model):
    msg_id = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    timestamp = models.DateField(default=datetime.date.today)
    version_range = models.CharField(max_length=50, default="*")
    ips_to_include = ArrayField(models.CharField(max_length=40), help_text="(comma-separated; leave empty to ignore IP)", default=list, blank=True)
    instances_to_include = ArrayField(models.CharField(max_length=40), help_text="(comma-separated; leave empty to ignore instance_id)", default=list, blank=True)
    link_url = models.CharField(max_length=250, blank=True)
    status = models.CharField(
        max_length=15,
        choices=[(c.name, c.value) for c in MessageStatuses],
        default=MessageStatuses.DISABLED.name,
    )
    i18n = JSONField(default=dict)

    def english_message(self):
        if "en" not in self.i18n:
            return ""
        return "{title}: {msg}".format(**self.i18n["en"])

    def clean(self):
        if "en" not in self.i18n:
            raise ValidationError("i18n field must contain at least 'en' key")
        for langdata in self.i18n.values():
            if set(langdata.keys()) != set(["msg", "title", "link_text"]):
                raise ValidationError(
                    "Each language object in i18n field must have exactly these keys: 'msg', 'title', 'link_text'"
                )
            if not isinstance(langdata["msg"], str):
                raise ValidationError(
                    "'msg' field in language objects under i18n field must contain a string"
                )
            if not isinstance(langdata["title"], str):
                raise ValidationError(
                    "'title' field in language objects under i18n field must contain a string"
                )
            if (
                not isinstance(langdata["link_text"], str)
                and langdata["link_text"] is not None
            ):
                raise ValidationError(
                    "'link_text' field in language objects under i18n field must contain a string or 'null'"
                )
