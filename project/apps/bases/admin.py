from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite as BaseAdminSite
from django.core.exceptions import FieldDoesNotExist


class AdminSite(BaseAdminSite):
    site_title = 'Project name'
    site_header = f'Project name — {settings.ENVIRONMENT}'
    index_title = 'Администрирование'
    enable_nav_sidebar = False


class BaseAdmin(admin.ModelAdmin):
    def get_prepopulated_fields(self, request, obj=None) -> dict:
        prepopulated_fields = super().get_prepopulated_fields(request, obj).copy()
        try:
            fields = self.get_fields(request, obj)
            if 'slug' in fields:
                target = self.model._meta.get_field('slug').target
                if target in fields:
                    prepopulated_fields['slug'] = [target]
        except FieldDoesNotExist:
            pass

        return prepopulated_fields


admin_site = AdminSite()
admin.site = admin_site
admin.sites.site = admin_site
admin.autodiscover()
