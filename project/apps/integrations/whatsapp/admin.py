from django.contrib import admin

from apps.bases.admin import BaseAdmin
from apps.integrations.whatsapp.models import WhatsAppTemplate, WhatsAppTemplateVersion, WhatsAppPhoneNumber


class WhatsAppTemplateVersionInline(admin.StackedInline):
    model = WhatsAppTemplateVersion

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(BaseAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = (
        WhatsAppTemplateVersionInline,
    )


@admin.register(WhatsAppPhoneNumber)
class WhatsAppPhoneNumberAdmin(BaseAdmin):
    list_display = ['vendor_id', 'name', 'display', 'default']
    search_fields = ['name', 'display']
