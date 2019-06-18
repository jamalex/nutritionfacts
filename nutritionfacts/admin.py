from django.contrib import admin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from .models import Pingback, Instance, IPLocation, Message

pyvers = [
    "2",
    "2.7",
    "2.7.1",
    "2.7.2",
    "2.7.3",
    "2.7.4",
    "2.7.5",
    "2.7.6",
    "2.7.7",
    "2.7.8",
    "2.7.9",
    "2.7.10",
    "2.7.11",
    "2.7.12",
    "2.7.13",
    "2.7.14",
    "2.7.15",
    "3",
    "3.4",
    "3.4.0",
    "3.4.1",
    "3.4.2",
    "3.4.3",
    "3.4.4",
    "3.4.5",
    "3.4.6",
    "3.4.7",
    "3.4.8",
    "3.4.9",
    "3.5",
    "3.5.0",
    "3.5.1",
    "3.5.2",
    "3.5.3",
    "3.5.4",
    "3.5.5",
    "3.5.6",
    "3.6",
    "3.6.0",
    "3.6.1",
    "3.6.2",
    "3.6.3",
    "3.6.4",
    "3.6.5",
    "3.6.6",
    "3.7",
    "3.7.0",
]


class ReadOnlyAdmin(admin.ModelAdmin):
    """Provides a read-only view of a model in Django admin."""

    readonly_fields = []

    def change_view(self, request, object_id, extra_context=None):
        """ customize add/edit form to remove save / save and continue """
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = False
        extra_context["show_save"] = False
        return super().change_view(request, object_id, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_readonly_fields(self, request, obj=None):
        return (
            list(self.readonly_fields)
            + [field.name for field in obj._meta.fields]
            + [field.name for field in obj._meta.many_to_many]
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DefaultModeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "default mode"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "default_mode"

    def lookups(self, request, model_admin):
        return (("yes", "Yes (public user)"), ("no", "No (LE user/dev)"))

    def queryset(self, request, queryset):
        attrname = None
        if hasattr(queryset.model, "mode"):
            attrname = "mode"
        elif hasattr(queryset.model, "last_mode"):
            attrname = "last_mode"
        if self.value() == "yes":
            return queryset.filter(**{attrname: ""})
        elif self.value() == "no":
            return queryset.exclude(**{attrname: ""})


class PythonVersionFilter(admin.SimpleListFilter):
    title = "python version"

    parameter_name = "python_version_prefix"

    def lookups(self, request, model_admin):
        prefix = request.GET.get(self.parameter_name, "")
        target_comp_count = min(2, prefix.count(".") + 1 if prefix else 0)
        matching = [
            ver
            for ver in pyvers
            if ver.startswith(prefix)
            if ver.count(".") == target_comp_count
        ]
        return tuple([(ver, ver) for ver in matching])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(python_version__startswith=self.value())


class PingbackAdmin(ReadOnlyAdmin):
    list_display = ("instance", "ip", "kolibri_version", "mode", "saved_at", "uptime")
    list_filter = (
        DefaultModeFilter,
        ("saved_at", DateRangeFilter),
        "kolibri_version",
        "mode",
    )
    date_hierarchy = "saved_at"


admin.site.register(Pingback, PingbackAdmin)


class InstanceAdmin(ReadOnlyAdmin):
    list_display = (
        "instance_id",
        "platform",
        "python_version",
        "database_id",
        "node_id",
        "first_seen",
        "last_seen",
        "last_mode",
    )
    list_filter = (
        DefaultModeFilter,
        ("first_seen", DateRangeFilter),
        ("last_seen", DateRangeFilter),
        PythonVersionFilter,
        "last_mode",
    )
    date_hierarchy = "first_seen"


admin.site.register(Instance, InstanceAdmin)


class IPLocationAdmin(ReadOnlyAdmin):
    list_display = (
        "ip_address",
        "host",
        "city",
        "subdivision",
        "country_name",
        "continent_name",
    )
    list_filter = ("continent_name", "country_name")


admin.site.register(IPLocation, IPLocationAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ("msg_id", "timestamp", "version_range", "status", "english_message")
    list_filter = ("status",)
    date_hierarchy = "timestamp"


admin.site.register(Message, MessageAdmin)
