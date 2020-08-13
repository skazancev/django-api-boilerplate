from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from . import models


@admin.register(models.EmailTemplate)
class EmailTemplateAdmin(SimpleHistoryAdmin):
    search_fields = ('subject', 'from_addr', 'type')
    list_display = ('type', 'subject', 'from_addr', 'send_after_hours', 'is_active')

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
            'admin/js/email_template_preview.js',
            "js/min/django_better_admin_arrayfield.min.js",
        )
        css = {"all": ("css/min/django_better_admin_arrayfield.min.css",)}
