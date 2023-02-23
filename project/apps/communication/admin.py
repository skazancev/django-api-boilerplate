from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.db import transaction
from django.utils import timezone
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

from apps.bases.admin import BaseAdmin
from apps.communication.tasks import send_communications
from utils.admin import pretty_typeform
from utils.core import clean_data
from . import models


def resend_communications(modeladmin, request, queryset):
    to_send = []
    for item in queryset:
        item.parent_id = item.id
        item.id = None
        item.trigger_type = models.UserFlow.Type.manual
        item.created = timezone.now()
        item.modified = timezone.now()
        item.agent = request.user
        item.save()
        to_send.append(item.id)

    transaction.on_commit(lambda: send_communications.delay(to_send))


resend_communications.short_description = "Resend communications"


@admin.register(models.CommunicationHistory)
class CommunicationHistoryAdmin(BaseAdmin):
    list_display = (
        'hash',
        'user',
        'direction',
        'target',
        'template_vendor',
        'type',
        'created',
        'sent',
        'user_email',
    )
    search_fields = ('user__email', 'agent__email')
    list_filter = ('direction', 'target', 'type', 'agent', 'sent')
    readonly_fields = ('created', 'formatted_response', 'formatted_context')
    list_select_related = ('user',)
    exclude = ('context', 'response')

    actions = (
        send_communications,
        resend_communications,
    )
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def changeform_view(self, request, *args, **kwargs):
        self.request = request
        return super().changeform_view(request, *args, **kwargs)

    def has_change_permission(self, request, obj=None):
        return False

    def formatted_response(self, obj):
        return pretty_typeform(obj.response)

    def formatted_context(self, obj):
        context = obj.context
        if not self.request.user.is_superuser:
            context = clean_data(context, replace_with='•••')

        return pretty_typeform(context)

    def user_email(self, obj):
        return obj.user.email


@admin.register(models.Template)
class TemplateAdmin(SimpleHistoryAdmin, BaseAdmin):
    search_fields = ('type', 'klaviyo_event__name')
    list_display = ('get_vendor_display', 'get_vendor_target', 'get_type_display', 'is_active', 'modified')
    autocomplete_fields = ('klaviyo_event', 'whatsapp_template')
    list_editable = ('is_active',)
    list_filter = ('type', 'vendor')
