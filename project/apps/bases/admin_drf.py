from functools import update_wrapper

from django_api_admin.sites import APIAdminSite as BaseAPIAdminSite

from api.admin.serializers import AdminUserSerializer


class APIAdminSite(BaseAPIAdminSite):
    user_serializer = AdminUserSerializer

    def api_admin_view(self, view, cacheable=False):
        admin_view = super().api_admin_view(view, cacheable)

        def inner(request, *args, **kwargs):
            view.__self__.request = request
            view.__self__.action = view.__name__
            view.__self__.object_id = kwargs.get('object_id')
            return admin_view(request, *args, **kwargs)

        return update_wrapper(inner, view)


api_admin_site = APIAdminSite(name='Boilerplate API Admin', include_auth=False)
