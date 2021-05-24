import json

from adminsortable.admin import SortableAdmin
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.db import transaction
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_json_widget.widgets import JSONEditorWidget
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer
from simple_history.admin import SimpleHistoryAdmin

from apps.bases.admin import BaseAdmin
from apps.communication.tasks import send_communications
from . import models


@admin.register(models.FAQ)
class ReviewAdmin(SimpleHistoryAdmin, SortableAdmin, BaseAdmin):
    list_display = ('__str__', 'created')
    readonly_fields = ('created',)


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
    list_display = ('hash', 'user', 'direction', 'target', 'trigger_type', 'created', 'sent')
    search_fields = ('user__email', 'agent__email')
    list_filter = ('direction', 'target', 'type', 'agent', 'sent')
    readonly_fields = ('created', 'pretty_typeform')
    list_select_related = ('user',)
    exclude = ('context',)

    actions = (
        resend_communications,
    )
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def pretty_typeform(self, obj):
        formatter = HtmlFormatter(style='colorful')
        data = json.dumps(obj.user_flow_action.flow.context, indent=2, ensure_ascii=False)
        response = highlight(data.encode('utf-8'), JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(models.Template)
class TemplateAdmin(SimpleHistoryAdmin, BaseAdmin):
    search_fields = ('subject', 'type', 'sendgrid_template__subject')
    list_display = ('get_subject', 'type', 'is_active', 'modified', 'sendgrid_template_id')
    autocomplete_fields = ('sendgrid_template',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += [
            ('Email preview', {
                'fields': [],
                'classes': ['collapse', 'email_preview'],
            })
        ]
        return fieldsets

    class Media:
        js = (
            "js/min/django_better_admin_arrayfield.min.js",
        )
        css = {"all": ("css/min/django_better_admin_arrayfield.min.css",)}


@admin.register(models.SendgridTemplate)
class SendgridTemplateAdmin(BaseAdmin):
    list_display = ('template_id', 'name', 'subject', 'is_active')
    readonly_fields = ('template_id', 'name', 'subject', 'active_version_id', 'is_active', 'preview_url_tag')
    search_fields = ('name', 'subject', '=template_id')

    def preview_url_tag(self, obj):
        return mark_safe(f'<img src="{obj.preview_url}"></img>')


@admin.register(models.FlowEvent)
class FlowEventAdmin(BaseAdmin):
    search_fields = ('title',)


class FlowActionInline(admin.StackedInline):
    model = models.FlowAction
    autocomplete_fields = ('template',)
    extra = 0
    fieldsets = (
        (None, {
            'fields': ('template', 'delay', 'delay_type', 'send_time')
        }),
    )


@admin.register(models.Flow)
class FlowAdmin(BaseAdmin):
    inlines = (FlowActionInline,)
    list_display = ('title', 'event')
    autocomplete_fields = ('event',)
    list_select_related = ('event',)
