from typing import Optional

from django_api_admin.options import APIModelAdmin as BaseAPIModelAdmin, InlineAPIModelAdmin

from api.admin.serializers import APIAdminSerializer


class APIModelAdminViewSet(BaseAPIModelAdmin):
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

    # add field type support
    def changelist_view(self, request, **kwargs):  # done
        return super().changelist_view(request, **kwargs)

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
