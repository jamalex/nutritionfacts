import datetime
import json
from ipware.ip import get_trusted_ip, get_ip


from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .geo import get_ip_info
from .models import Pingback, IPLocation, Instance

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

    # build an Instance objects if we don't already have one, and update timestamps
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
    instance.save()

    # create the Pingback objects itself
    Pingback.objects.create(
        instance_id_old=instance_id,
        instance=instance,
        kolibri_version=kolibri_version,
        mode=payload.get("mode") or ("dev" if "dev" in kolibri_version else ""),
        ip=iplocation,
        platform=payload.get("platform") or "",
        python_version=payload.get("sysversion") or "",
        database_id=payload.get("database_id") or "",
        node_id=payload.get("node_id") or "",
        uptime=payload.get("uptime") or None,
        saved_at=saved_at,
    )

    return HttpResponse("")


def health_check(request):

    return HttpResponse("OK")
