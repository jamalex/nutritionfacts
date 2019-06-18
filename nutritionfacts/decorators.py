import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

# from https://coderwall.com/p/k8vb_a/returning-json-jsonp-from-a-django-view-with-a-little-decorator-help
def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """

    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        data = json.dumps(objects, indent=4, cls=DjangoJSONEncoder)
        if "callback" in request.GET:
            # a jsonp response!
            data = "%s(%s);" % (request.GET["callback"], data)
            return HttpResponse(data, "text/javascript")
        return HttpResponse(data, "application/json")

    return decorator
