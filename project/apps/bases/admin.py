from django.conf import settings
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist

from api_admin.options import APIModelAdmin
from api_admin.sites import api_admin_site


class AdminSite(admin.AdminSite):
    site_title = settings.COMPANY_NAME
    site_header = f'{settings.COMPANY_NAME} — {settings.ENVIRONMENT}'
    index_title = 'Администрирование'
    enable_nav_sidebar = False

    def register(self, model_or_iterable, admin_class=None, **options):
        super().register(model_or_iterable, admin_class, **options)
        api_admin_site.register(
            model_or_iterable,
            admin_class=type(
                f'API{admin_class.__name__}',
                (APIModelAdmin, admin_class),
                options
            ) if admin_class else None,
        )


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


admin_site = AdminSite(name=settings.COMPANY_NAME)

admin.site = admin_site
admin.sites.site = admin_site
admin.autodiscover()
