from django.contrib import admin
from .models import Pingback, Instance, IPLocation


class DefaultModeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'default mode'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'default_mode'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes (public user)'),
            ('no', 'No (LE user/dev)'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        attrname = None
        if hasattr(queryset.model, 'mode'):
            attrname = 'mode'
        elif hasattr(queryset.model, 'last_mode'):
            attrname = 'last_mode'
        if self.value() == 'yes':
            return queryset.filter(**{attrname: ''})
        elif self.value() == 'no':
            return queryset.exclude(**{attrname: ''})


class PingbackAdmin(admin.ModelAdmin):
    list_display = ('instance', 'ip', 'kolibri_version', 'mode', 'saved_at', 'uptime')
    list_filter = (DefaultModeFilter, 'kolibri_version', 'mode')
    date_hierarchy = 'saved_at'
admin.site.register(Pingback, PingbackAdmin)


class InstanceAdmin(admin.ModelAdmin):
    list_display = ('instance_id', 'platform', 'python_version', 'database_id', 'node_id', 'first_seen', 'last_seen', 'last_mode')
    list_filter = (DefaultModeFilter, 'python_version', 'last_mode')
    date_hierarchy = 'first_seen'
admin.site.register(Instance, InstanceAdmin)


class IPLocationAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'host', 'city', 'subdivision', 'country_name', 'continent_name')
    list_filter = ('continent_name', 'country_name')
admin.site.register(IPLocation, IPLocationAdmin)


