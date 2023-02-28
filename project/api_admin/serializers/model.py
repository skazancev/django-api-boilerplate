from typing import TYPE_CHECKING

from django.forms import ModelForm
from rest_framework import serializers

from ..fields import APIAdminReadOnlyField
from api.serializers import ModelSerializer
from utils.drf import get_django_form_kwargs, django_drf_fields_map
from ..utils import get_serializer_for_admin

if TYPE_CHECKING:
    from ..options import APIModelAdmin


class APIAdminSerializer(ModelSerializer):
    model_admin: 'APIModelAdmin'
    admin_form: ModelForm
    _api_action: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_inlines(self, obj) -> list:
        inlines = zip(*self.model_admin._create_formsets(
            self._request,
            self.instance,
            change=False,
        ))
        result = []
        for formset, inline_instance in inlines:
            serializer = get_serializer_for_admin(
                model_admin=inline_instance,
                action=self._api_action,
                request=self._request,
                obj=obj,
                changelist=False
            )
            result.append(serializer(formset.queryset, many=True, context=self.context).data)

        return result

    def build_unknown_field(self, field_name, model_class):
        if field_name == 'inlines':
            return serializers.SerializerMethodField, {}

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
