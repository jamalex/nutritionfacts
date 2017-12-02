from django.db import models


class Pingback(models.Model):

    # The unique identifier for this Kolibri instance
    instance_id = models.CharField(max_length=32)

    # What Kolibri version is this ping from
    kolibri_version = models.CharField(max_length=50)

    # the "mode" the Kolibri instance is running in (e.g. "source", "demo", "production")
    mode = models.CharField(max_length=30, blank=True)

    # The ping may be from an IPv6 address, whose max length is 45 characters
    ip_address = models.CharField(max_length=45, blank=True)

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
