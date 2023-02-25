from typing import TYPE_CHECKING

from django.forms import ModelForm
from rest_framework import serializers

from api.admin.fields import APIAdminReadOnlyField
from utils.drf import get_django_form_kwargs, django_drf_fields_map

if TYPE_CHECKING:
    from api.admin.viewsets import APIModelAdminViewSet


class APIAdminSerializer(serializers.ModelSerializer):
    model_admin: 'APIModelAdminViewSet'
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
