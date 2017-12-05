import json
from ipware.ip import get_trusted_ip, get_ip

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Pingback


@csrf_exempt
@require_http_methods(["POST"])
def pingback(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return HttpResponseBadRequest(
            "Sorry, please send a"
            " valid JSON object."
        )
    
    Pingback.objects.create(
        instance_id=payload.get("instance_id") or "",
        kolibri_version=payload.get("version") or "",
        mode=payload.get("mode") or "",
        ip_address=get_trusted_ip(request) or get_ip(request),
        platform=payload.get("platform") or "",
        python_version=payload.get("sysversion") or "",
        database_id=payload.get("database_id") or "",
        node_id=payload.get("node_id") or "",
        uptime=payload.get("uptime") or None,
    )

    return HttpResponse("")
