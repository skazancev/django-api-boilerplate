from django.contrib import admin

from utils.admin import pretty_typeform
from .models import WebhookData
from ..bases.admin import BaseAdmin, admin_site


@admin.register(WebhookData, site=admin_site)
class WebhookDataAdmin(BaseAdmin):
    list_filter = ('source',)
    list_display = ('source', 'created', 'id', 'short_payload', 'remote_ip')
    exclude = ('content', 'content_search')
    readonly_fields = ('pretty_typeform',)
    search_fields = ('content_search',)

    def pretty_typeform(self, obj):
        return pretty_typeform(obj.content)

    def short_payload(self, obj):
        return pretty_typeform(obj.content, cut=True)

    def get_search_results(self, request, queryset, search_term):
        # overridden because django does not support SearchVectorField
        if search_term:
            return queryset.filter(content_search=search_term), True
        return queryset, False
