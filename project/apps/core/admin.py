from django.contrib import admin

from . import models
from ..bases.admin import BaseAdmin, admin_site


@admin.register(models.Config, site=admin_site)
class ConfigAdmin(BaseAdmin):
    list_display = ('type', 'value')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(visible=True)
