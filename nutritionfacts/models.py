from django.db import models

from .geo import get_ip_info

# SPECIAL_HOST_MODES = {
#     "ucsd.edu": "ucsd",
#     ""
# }

class Pingback(models.Model):

    # The unique identifier for this Kolibri instance
    instance_id = models.CharField(max_length=32)

    # What Kolibri version is this ping from
    kolibri_version = models.CharField(max_length=50)

    # the "mode" the Kolibri instance is running in (e.g. "source", "demo", "production")
    mode = models.CharField(max_length=30, blank=True)

    ip = models.ForeignKey("IPLocation", blank=True, null=True, on_delete=models.PROTECT)

    # The operating system this Kolibri instance is running on
    platform = models.CharField(max_length=150, blank=True)

    # The python version running this Kolibri instance
    python_version = models.CharField(max_length=100, blank=True)

    # The database-specific id of the Kolibri instance
    database_id = models.CharField(max_length=32, blank=True)

    # The unique device identifier based on the MAC address
    node_id = models.CharField(max_length=32, blank=True)

    # The date this ping was received
    saved_at = models.DateTimeField(auto_now_add=True)

    # How long the server has been running (in minutes)
    uptime = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.ip_id = self.ip_id or self.ip_address
        try:
            ip = self.ip
        except IPLocation.DoesNotExist:
            self.ip = IPLocation.objects.create(ip_address=self.ip_id, **get_ip_info(self.ip_id))

        super(Pingback, self).save(*args, **kwargs)


class IPLocation(models.Model):

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
