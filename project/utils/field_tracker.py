from typing import Union

from django.db.models.fields.files import FileDescriptor
from django.db.models.query_utils import DeferredAttribute
from model_utils import FieldTracker
from model_utils.tracker import FieldInstanceTracker, DescriptorMixin


class CustomFieldInstanceTracker(FieldInstanceTracker):
    def init_deferred_fields(self):
        self.instance._deferred_fields = set()
        if hasattr(self.instance, '_deferred') and not self.instance._deferred:
            return

        class DeferredAttributeTracker(DescriptorMixin, DeferredAttribute):
            tracker_instance = self

        class FileDescriptorTracker(DescriptorMixin, FileDescriptor):
            tracker_instance = self

            def _get_field_name(self):
                return self.field.name

        self.instance._deferred_fields = self.instance.get_deferred_fields()
        for field in self.instance._deferred_fields:
            field_obj = getattr(self.instance.__class__, field)
            if isinstance(field_obj, FileDescriptor):
                field_tracker = FileDescriptorTracker(field_obj.field)
                setattr(self.instance.__class__, field, field_tracker)
            else:
                # only the deleted None has changed, original line is
                # field_tracker = DeferredAttributeTracker(field_obj.field_name, None)
                field_tracker = DeferredAttributeTracker(field_obj.field_name)
                setattr(self.instance.__class__, field, field_tracker)

    def has_changed(self, *fields: Union[str, list], allow_any=True, has_prev_value=False) -> bool:
        """ add support to check multiple fields in one call """
        if not has_prev_value and (not self.instance.pk or self.instance._state.adding):
            return True

        changed = {
            field
            for field in fields
            if (not has_prev_value or self.previous(field)) and self.previous(field) != self.get_field_value(field)
        }

        if allow_any and changed:
            return True
        return set(fields) == changed


class CustomFieldTracker(FieldTracker):
    tracker_class = CustomFieldInstanceTracker
