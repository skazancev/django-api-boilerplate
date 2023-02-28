from django.contrib.admin.utils import lookup_field
from rest_framework.fields import ReadOnlyField


class APIAdminReadOnlyField(ReadOnlyField):
    def __init__(self, model_admin, **kwargs):
        super().__init__(**kwargs)
        self.model_admin = model_admin

    def get_attribute(self, instance):
        return lookup_field(self.field_name, instance, model_admin=self.model_admin)[2]
