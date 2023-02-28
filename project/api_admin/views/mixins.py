from ..utils import get_form_fields


class CRUDMixin:
    def get_inlines(self, request,  model_admin, obj=None):
        inlines = list()

        for inline_admin in model_admin.get_inline_instances(request, obj=obj):
            serializer_class = inline_admin.get_serializer_class(request)
            serializer = serializer_class()
            inlines.append(
                {
                    'name': inline_admin.model._meta.verbose_name_plural,
                    'object_name': inline_admin.model._meta.verbose_name,
                    'admin_name':  '_'.join([
                        inline_admin.parent_model._meta.app_label,
                        inline_admin.parent_model._meta.model_name,
                        inline_admin.model._meta.model_name,
                    ]),
                    'fields': get_form_fields(serializer),
                    'config': self.get_config(request, inline_admin, obj=obj)
                }
            )

        return inlines

    def get_config(self, request, model_admin, obj=None):
        return {
            'name': model_admin.model._meta.verbose_name_plural,
            'object_name': model_admin.model._meta.verbose_name,
            'admin_name': '_'.join([
                model_admin.model._meta.app_label,
                model_admin.model._meta.model_name,
            ]),
            'fieldsets': model_admin.get_fieldsets(request, obj=obj),
            'read_only_fields': model_admin.get_readonly_fields(request, obj=obj),
            'save_on_top': getattr(model_admin, 'save_on_top', None),
            'save_as': getattr(model_admin, 'save_as', None),
            'save_as_continue': getattr(model_admin, 'save_as_continue', None),
            'view_on_site': getattr(model_admin, 'view_on_site', None),
        }
