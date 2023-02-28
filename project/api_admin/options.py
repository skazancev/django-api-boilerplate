from typing import Optional

from django.contrib.admin.options import InlineModelAdmin, ModelAdmin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth import get_permission_codename
from django.db import router, transaction
from django.http import HttpRequest
from rest_framework import serializers

from utils.cache import cached_method
from . import views as api_views
from .serializers import ActionSerializer
from .utils import get_serializer_for_admin


class BaseAPIModelAdmin:
    """
    Shared behavior between APIModelAdmin, APIInlineModelAdmin.
    """
    request: HttpRequest
    object_id: Optional[int]
    action: str

    # these are the options used in the change/add forms
    # of the model_admin

    @cached_method
    def get_object(self, request=None, object_id=None, from_field=None):
        if request is None:
            request = self.request

        if object_id is None and self.object_id:
            object_id = self.object_id

        return super().get_object(request, object_id, from_field)

    @property
    def get_form_fieldsets(self):
        return self.get_fieldsets(self.request, self.get_object())

    def get_fields_list(self, request, obj=None):
        if self.action in ['list_view', 'changelist_view']:
            fieldsets_fields = list(self.list_display)
        else:
            fieldsets_fields = flatten_fieldsets(self.get_fieldsets(request, obj))

        if self.action == 'detail_view':
            fieldsets_fields.append('inlines')

        fieldsets_fields.insert(0, 'pk')
        # get excluded fields
        excluded = self.get_exclude(request, obj)
        exclude = list(excluded) if excluded is not None else []
        # get read only fields
        # subtract excluded fields from fieldsets_fields
        return [field for field in fieldsets_fields if field not in exclude]

    def get_serializer_class(self, request, obj=None, changelist=False):
        return get_serializer_for_admin(self, self.action, request, obj or self.get_object(request=request), changelist)

    def get_permission_map(self, request, obj=None):
        """
        return a dictionary of user permissions in this module.
        """

        return {
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
            'has_view_permission': self.has_view_permission(request),
            'has_view_or_change_permission': self.has_view_or_change_permission(request),
            'has_module_permission': self.has_module_permission(request),
        }

    def has_add_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('add', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('change', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('delete', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_view_permission(self, request, obj=None):
        opts = self.opts
        codename_view = get_permission_codename('view', opts)
        codename_change = get_permission_codename('change', opts)
        return (
            request.user.has_perm('%s.%s' % (opts.app_label, codename_view)) or
            request.user.has_perm('%s.%s' % (opts.app_label, codename_change))
        )

    def has_view_or_change_permission(self, request, obj=None):
        return self.has_view_permission(request) or self.has_change_permission(request)

    def has_module_permission(self, request):
        return request.user.has_module_perms(self.opts.app_label)

    @property
    def is_inline(self):
        return isinstance(self, InlineModelAdmin)

    def list_view(self, request):
        defaults = {
            'serializer_class': self.get_serializer_class(request),
            'permission_classes': self.admin_site.default_permission_classes,
        }
        return api_views.ListView.as_view(**defaults)(request, self)

    def detail_view(self, request, object_id):
        defaults = {
            'serializer_class': self.get_serializer_class(request),
            'permission_classes': self.admin_site.default_permission_classes,
        }
        return api_views.DetailView.as_view(**defaults)(request, object_id, self)

    def add_view(self, request, **kwargs):
        defaults = {
            'serializer_class': self.get_serializer_class(request),
            'permission_classes': self.admin_site.default_permission_classes,
        }
        with transaction.atomic(using=router.db_for_write(self.model)):
            return api_views.AddView.as_view(**defaults)(request, self, **kwargs)

    def change_view(self, request, object_id, **kwargs):
        defaults = {
            'serializer_class': self.get_serializer_class(request),
            'permission_classes': self.admin_site.default_permission_classes,
        }
        with transaction.atomic(using=router.db_for_write(self.model)):
            return api_views.ChangeView.as_view(**defaults)(request, object_id, self, **kwargs)

    def delete_view(self, request, object_id, **kwargs):
        defaults = {
            'permission_classes': self.admin_site.default_permission_classes
        }
        with transaction.atomic(using=router.db_for_write(self.model)):
            return api_views.DeleteView.as_view(**defaults)(request, object_id, self, **kwargs)


class APIModelAdmin(BaseAPIModelAdmin, ModelAdmin):
    """
    exposes django.contrib.admin.options.ModelAdmin as a restful api.
    everything that is ui specific is handled by the ui
    filtering is also handled by the ui
    """
    action_serializer = ActionSerializer

    # these are the admin options used to customize the change list page interface
    # server-side customizations like list_select_related and actions are not included
    changelist_options = [
        # actions options
        'actions_on_top', 'actions_on_bottom', 'actions_selection_counter',

        # display options
        'empty_value_display', 'list_display', 'list_display_links', 'list_editable',
        'exclude',

        # pagination
        'show_full_result_count', 'list_per_page', 'list_max_show_all',

        # filtering, sorting and searching
        'date_hierarchy', 'search_help_text', 'sortable_by', 'search_fields',
        'preserve_filters',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_on_site = False if not self.admin_site.include_view_on_site_view else self.view_on_site

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        return tuple(
            type(f'API{inline.__name__}', (InlineAPIModelAdmin, inline), {
                'reqeust': self.request,
                'action': self.action,
                'object_id': self.object_id,
            })
            for inline in inlines
        )

    def get_action_serializer(self, request):
        return type('%sActionSerializer' % self.__class__.__name__, (ActionSerializer,), {
            'action': serializers.ChoiceField(choices=[*self.get_action_choices(request)]),
            'selected_ids': serializers.MultipleChoiceField(choices=[*self.get_selected_ids(request)])
        })

    def get_selected_ids(self, request):
        queryset = self.get_queryset(request)
        choices = []
        for item in queryset:
            choices.append((f'{item.pk}', f'{str(item)}'))
        return choices

    def get_urls(self):
        from django.urls import path

        info = self.model._meta.app_label, self.model._meta.model_name
        admin_view = self.admin_site.api_admin_view

        urlpatterns = [
            path('list/', admin_view(self.list_view), name='%s_%s_list' % info),
            path('changelist/', admin_view(self.changelist_view),
                 name='%s_%s_changelist' % info),
            path('perform_action/', admin_view(self.handle_action_view),
                 name='%s_%s_perform_action' % info),
            path('add/', admin_view(self.add_view), name='%s_%s_add' % info),
            path('<path:object_id>/detail/', admin_view(self.detail_view),
                 name='%s_%s_detail' % info),
            path('<path:object_id>/delete/', admin_view(self.delete_view),
                 name='%s_%s_delete' % info),
            path('<path:object_id>/history/',
                 admin_view(self.history_view), name='%s_%s_history' % info),
            path('<path:object_id>/change/', admin_view(self.change_view),
                 name='%s_%s_change' % info),
        ]

        return urlpatterns

    def changelist_view(self, request, **kwargs):
        defaults = {
            'permission_classes': self.admin_site.default_permission_classes
        }
        return api_views.ChangeListView.as_view(**defaults)(request, self)

    def handle_action_view(self, request):
        defaults = {
            'permission_classes': self.admin_site.default_permission_classes,
            'serializer_class': self.get_action_serializer(request)
        }
        return api_views.HandleActionView.as_view(**defaults)(request, self)

    def history_view(self, request, object_id, extra_context=None):
        defaults = {
            'permission_classes': self.admin_site.default_permission_classes,
            'serializer_class': self.admin_site.log_entry_serializer,
        }
        return api_views.HistoryView.as_view(**defaults)(request, object_id, self)


class InlineAPIModelAdmin(BaseAPIModelAdmin, InlineModelAdmin):
    """
    Edit models connected with a relationship in one page
    """
    admin_style = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_form(self, request, obj=None):
        return self.get_formset(request, obj).form

    def get_object(self, request=None, object_id=None, from_field=None):
        queryset = self.get_queryset(request)
        model = queryset.model
        try:
            return queryset.get(pk=object_id or self.object_id)
        except model.DoesNotExist:
            return None

    def get_urls(self):
        from django.urls import path

        info = (self.parent_model._meta.app_label, self.parent_model._meta.model_name,
                self.opts.app_label, self.opts.model_name)
        admin_view = self.admin_site.api_admin_view

        return [
            path('list/', admin_view(self.list_view),
                 name='%s_%s_%s_%s_list' % info),
            path('add/', admin_view(self.add_view),
                 name='%s_%s_%s_%s_add' % info),
            path('<path:object_id>/detail/', admin_view(self.detail_view),
                 name='%s_%s_%s_%s_detail' % info),
            path('<path:object_id>/change/', admin_view(self.change_view),
                 name='%s_%s_%s_%s_change' % info),
            path('<path:object_id>/delete/', admin_view(self.delete_view),
                 name='%s_%s_%s_%s_delete' % info),
        ]

    @property
    def urls(self):
        return self.get_urls()
