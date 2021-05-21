from django.contrib.admin.apps import AdminConfig as BaseAdminConfig


class AdminConfig(BaseAdminConfig):
    default_site = 'apps.bases.admin.AdminSite'

    def ready(self):
        from . import signals  # noqa: F401
