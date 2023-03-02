from django.contrib import admin

from apps.bases.admin import BaseAdmin
from apps.integrations.whatsapp.models import WhatsAppTemplate, WhatsAppTemplateVersion, WhatsAppPhoneNumber, \
    WhatsAppMessage, WhatsAppMessageEvent


class WhatsAppTemplateVersionInline(admin.StackedInline):
    model = WhatsAppTemplateVersion
    extra = 1

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False


@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(BaseAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = (
        WhatsAppTemplateVersionInline,
    )


@admin.register(WhatsAppPhoneNumber)
class WhatsAppPhoneNumberAdmin(BaseAdmin):
    list_display = ['vendor_id', 'name', 'display', 'type', 'default']
    search_fields = ['vendor_id', 'name', 'display']
    list_filter = ['type']


class WhatsAppMessageEventInline(admin.StackedInline):
    model = WhatsAppMessageEvent
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(BaseAdmin):
    list_display = ['vendor_id', 'from_number', 'type', 'date']
    autocomplete_fields = ('from_number', 'to_number')
    inlines = [
        WhatsAppMessageEventInline,
    ]
