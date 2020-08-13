from django.contrib import messages
from django.db import transaction, connection, models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.timezone import template_localtime
from environ import ImproperlyConfigured
from simple_history.admin import SimpleHistoryAdmin, SIMPLE_HISTORY_EDIT


class CustomSimpleHistoryAdmin(SimpleHistoryAdmin):
    history_list_changes_view = True

    def history_form_view(self, request, object_id, version_id, extra_context=None):
        if SIMPLE_HISTORY_EDIT:
            change_history = True
        else:
            change_history = False

        if not connection.features.uses_savepoints:
            raise ImproperlyConfigured("Cannot use History with a database that does not support savepoints.")
        with transaction.atomic():
            original_opts = self.model._meta

            model = getattr(self.model, self.model._meta.simple_history_manager_attribute).model
            version = get_object_or_404(
                model, **{original_opts.pk.attname: object_id, "history_id": version_id}
            )

            url_triplet = self.admin_site.name, original_opts.app_label, original_opts.model_name
            extra_context = extra_context or {}
            extra_context.update({
                "title": self.history_form_view_title(version.instance),
                "changelist_url": reverse("%s:%s_%s_changelist" % url_triplet),
                "change_url": reverse("%s:%s_%s_change" % url_triplet, args=(version.instance.pk,)),
                "history_url": reverse("%s:%s_%s_history" % url_triplet, args=(version.instance.pk,)),
                "change_history": change_history,
            })
            models.Model.save_base(version.instance, raw=True)
            response = self.changeform_view(request, str(version.instance.pk), request.path, extra_context)
            if request.method == "POST" and response.status_code == 302:
                messages.success(
                    request,
                    _("Reverted to previous version, saved on %(datetime)s") % {
                        "datetime": localize(template_localtime(version.history_date)),
                    }
                )
            else:
                response.template_name = self.object_history_form_template
                response.render()
                transaction.set_rollback(True)

        return response

    def history_view(self, request, object_id, extra_context=None):
        if self.history_list_changes_view:
            return self.history_view_with_changes(request, object_id, extra_context)

        return super().history_view(request, object_id, extra_context)

    def history_view_with_changes(self, request, object_id, extra_context=None):
        def xstr(val):
            if isinstance(val, (list, tuple, set)):
                val = ', '.join(map(str, val))

            return val or ''

        @transaction.atomic
        def get_action_with_diff_list(action_list):  # noqa
            old_record = None
            new_action_list = []
            for action in action_list[::-1]:
                if old_record:
                    changes = action.diff_against(old_record).changes
                    changes_list = [
                        f'<b>{change.field}</b>:'
                        f'<br/>New: {xstr(change.new)}'
                        f'<br/>Old: {xstr(change.old)}'
                        for change in changes
                    ]
                    action.delta_display = mark_safe('<br/>'.join(changes_list))
                old_record = action
                new_action_list.append(action)
            transaction.set_rollback(True)

            return new_action_list[::-1]

        model = self.model
        history = getattr(model, model._meta.simple_history_manager_attribute)
        action_list = history.filter(**{model._meta.pk.name: object_id})
        if not isinstance(history.model.history_user, property):
            action_list = action_list.select_related('history_user')
        extra_context = extra_context or {}

        extra_context['action_list'] = get_action_with_diff_list(action_list)
        if 'delta_display' not in getattr(self, 'history_list_display', []):
            self.history_list_display = list(getattr(self, 'history_list_display', [])) + ['delta_display']

        return super().history_view(request, object_id, extra_context)
