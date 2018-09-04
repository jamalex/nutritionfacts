from django.db import models


class Pingback(models.Model):

    class Meta:
        verbose_name = "Pingback"

    instance = models.ForeignKey("Instance", blank=True, null=True, related_name="pingbacks", on_delete=models.PROTECT)

    ip = models.ForeignKey("IPLocation", blank=True, null=True, related_name="pingbacks", on_delete=models.PROTECT)

    # What Kolibri version is this ping from
    kolibri_version = models.CharField(max_length=50)

    # the "mode" the Kolibri instance is running in (e.g. "source", "demo", "production")
    mode = models.CharField(max_length=30, blank=True)

    # The date this ping was received
    saved_at = models.DateTimeField()

    # How long the server has been running (in minutes)
    uptime = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "{instance} from {ip} at {saved_at:%Y-%m-%d %H:%M}".format(instance=(self.instance_id or "?")[:6], ip=self.ip_id, saved_at=self.saved_at)


class Instance(models.Model):

    class Meta:
        verbose_name = "Instance"

    # The unique identifier for this Kolibri instance
    instance_id = models.CharField(max_length=32, primary_key=True)

    # The operating system this Kolibri instance is running on
    platform = models.CharField(max_length=150, blank=True)

    # The python version running this Kolibri instance
    python_version = models.CharField(max_length=100, blank=True)

    # The database-specific id of the Kolibri instance
    database_id = models.CharField(max_length=32, blank=True)

    # The unique device identifier based on the MAC address
    node_id = models.CharField(max_length=32, blank=True)

    first_seen = models.DateTimeField(blank=True, null=True)

    last_seen = models.DateTimeField(blank=True, null=True)

    last_mode = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return "{instance}, on {platform}, with Python {python}".format(instance=(self.instance_id or "?")[:6], platform=self.platform, python=self.python_version.split()[0])

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
        return "{ip} in {city}, {country}".format(ip=self.ip_address, city=self.city or "?", country=self.country_name or "?")
