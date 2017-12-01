from django.db import models


class Pingback(models.Model):

    # The unique identifier for this Kolibri instance
    # TODO: what's the max length of the instance id?
    instance_id = models.CharField(max_length=100)

    # What kolibri version is this ping from
    kolibri_version = models.CharField(max_length=30)

    # The ping may be from an IPv6 address, whose max length is 45 characters
    ip_address = models.CharField(max_length=45)

    # The operating system this Kolibri instance is running on
    platform = models.CharField(max_length=10)

    # The python version running this Kolibri instance
    python_version = models.CharField(max_length=10)

    # ??
    database_id = models.CharField(max_length=50)

    # ??
    system_id = models.CharField(max_length=50)

    # The date this ping has been received
    saved_at = models.DateField(auto_now_add=True)
