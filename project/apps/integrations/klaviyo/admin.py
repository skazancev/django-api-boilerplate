from django.contrib import admin

from . import models
from ...bases.admin import BaseAdmin


@admin.register(models.KlaviyoEvent)
class KlaviyoEventAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def has_change_permission(self, request, obj=None):
        return False
