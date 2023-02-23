from functools import update_wrapper
from typing import Optional

from django.contrib.admin.utils import lookup_field
from django.forms import ModelForm
from django_api_admin.options import APIModelAdmin as BaseAPIModelAdmin, InlineAPIModelAdmin
from django_api_admin.sites import APIAdminSite as BaseAPIAdminSite
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from utils.drf import get_django_form_kwargs, django_drf_fields_map


class APIModelAdmin(BaseAPIModelAdmin):
    object_id: Optional[int]
    action: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inlines = self.api_inlines

    @property
    def api_inlines(self):
        return (
            type(f'API{inline.__name__}', (inline, InlineAPIModelAdmin), {})
            for inline in self.inlines
        )

    def get_serializer_class(self, request, obj=None, changelist=False):
        admin_form = None
        if self.action in ['change_view', 'add_view']:
            admin_form = self.get_form(request, obj)(instance=obj)

        if obj is None and self.object_id:
            obj = self.get_object(request, self.object_id)

        serializer_class = super().get_serializer_class(request, obj, changelist)
        serializer_class = type(
            serializer_class.__name__,
            (APIAdminSerializer, serializer_class),
            {
                'model_admin': self,
                'admin_form': admin_form
            },
        )

        return serializer_class

    # make list_view workable and add pagination
    def list_view(self, request):  # done
        return super().changelist_view(request)

    def detail_view(self, request, object_id):  # done
        return super().detail_view(request, object_id)

    def change_view(self, request, object_id, **kwargs):  # done
        return super().change_view(request, object_id, **kwargs)

    # fix config (replace fieldsets with get_fieldsets)
    def add_view(self, request, **kwargs):  # done
        return super().add_view(request, **kwargs)

    def delete_view(self, request, object_id, **kwargs):  # done
        return super().delete_view(request, object_id, **kwargs)

    # works with internal django log entry, add support for django-simple-history
    def history_view(self, request, object_id, extra_context=None):  # done
        return super().history_view(request, object_id, extra_context)

    def handle_action_view(self, request):  # to do
        return super().handle_action_view(request)


class APIAdminSite(BaseAPIAdminSite):
    def api_admin_view(self, view, cacheable=False):
        admin_view = super().api_admin_view(view, cacheable)

        def inner(request, *args, **kwargs):
            view.__self__.request = request
            view.__self__.action = view.__name__
            view.__self__.object_id = kwargs.get('object_id')
            return admin_view(request, *args, **kwargs)

        return update_wrapper(inner, view)


class APIAdminReadOnlyField(ReadOnlyField):
    def __init__(self, model_admin, **kwargs):
        super().__init__(**kwargs)
        self.model_admin = model_admin

    def get_attribute(self, instance):
        return lookup_field(self.field_name, instance, model_admin=self.model_admin)[2]


class APIAdminSerializer(serializers.ModelSerializer):
    model_admin: APIModelAdmin
    admin_form: ModelForm

    def build_field(self, field_name, info, model_class, nested_depth):
        return super().build_field(field_name, info, model_class, nested_depth)

    def build_unknown_field(self, field_name, model_class):
        if hasattr(self.model_admin, field_name):
            field_class = APIAdminReadOnlyField
            field_kwargs = {
                'model_admin': self.model_admin,
            }
            return field_class, field_kwargs

        elif self.admin_form and (form_field := self.admin_form.fields.get(field_name)):
            if field := django_drf_fields_map.get(form_field.__class__):
                return field, get_django_form_kwargs(form_field)

        return super().build_unknown_field(field_name, model_class)


api_admin_site = APIAdminSite(name='Boilerplate API Admin', include_auth=False)
