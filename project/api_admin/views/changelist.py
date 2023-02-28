from django.contrib.admin.options import (IncorrectLookupParameters)
from django.contrib.admin.utils import label_for_field, lookup_field
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db.models import Model
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from ..utils import get_form_fields


# model admin wide views
class ChangeListView(APIView):
    permission_classes = []

    def get(self, request, model_admin):
        try:
            cl = model_admin.get_changelist_instance(request)
        except IncorrectLookupParameters as e:
            raise NotFound(str(e))
        columns = self.get_columns(request, cl)
        rows = self.get_rows(request, cl)
        config = self.get_config(request, cl)
        return Response({'config': config, 'columns': columns, 'rows': rows},
                        status=status.HTTP_200_OK)

    def get_columns(self, request, cl):
        """
        return changelist columns or headers.
        """
        columns = []
        for field_name in self.get_fields_list(request, cl):
            text, attr = label_for_field(field_name, cl.model, model_admin=cl.model_admin, return_attr=True)
            columns.append({'field': field_name, 'headerName': text})
        return columns

    def get_rows(self, request, cl):
        """
        Return changelist rows actual list of data.
        """
        rows = []
        # generate changelist attributes (e.g result_list, paginator, result_count)
        cl.get_results(request)
        empty_value_display = cl.model_admin.get_empty_value_display()
        for result in cl.result_list:
            model_info = (cl.model_admin.admin_site.name, type(result)._meta.app_label, type(result)._meta.model_name)
            row = {
                'change_url': reverse('%s:%s_%s_change' % model_info, kwargs={'object_id': result.pk}, request=request),
                'id': result.pk,
                'cells': {}
            }

            for field_name in self.get_fields_list(request, cl):
                try:
                    _, _, value = lookup_field(
                        field_name, result, cl.model_admin)

                    # if the value is a Model instance get the string representation
                    if value and isinstance(value, Model):
                        result_repr = str(value)
                    else:
                        result_repr = value

                    # if there are choices display the choice description string instead of the value
                    try:
                        model_field = result._meta.get_field(field_name)
                        choices = getattr(model_field, 'choices', None)
                        if choices:
                            result_repr = [
                                choice for choice in choices if choice[0] == value
                            ][0][1]
                    except FieldDoesNotExist:
                        pass

                    # if the value is null set result_repr to empty_value_display
                    if value is None:
                        result_repr = empty_value_display

                except ObjectDoesNotExist:
                    result_repr = empty_value_display

                row['cells'][field_name] = result_repr
            rows.append(row)
        return rows

    def get_config(self, request, cl):
        config = {}

        # add the ModelAdmin attributes that the changelist uses
        for option_name in cl.model_admin.changelist_options:
            config[option_name] = (getattr(cl.model_admin, option_name, None))

        # changelist pagination attributes
        config['full_count'] = cl.full_result_count
        config['result_count'] = cl.result_count

        # a list of action names and choices
        config['action_choices'] = cl.model_admin.get_action_choices(
            request, [])

        # a list of filters titles and choices
        filters_spec, _, _, _, _ = cl.get_filters(request)
        if filters_spec:
            config['filters'] = [
                {"title": filter.title, "choices": filter.choices(cl)} for filter in filters_spec]
        else:
            config['filters'] = []

        # a dict of serializer fields attributes for every field in list editable
        editing_fields = {}
        serializer_class = cl.model_admin.get_serializer_class(
            request, changelist=True)
        serializer = serializer_class()
        form_fields = get_form_fields(serializer)

        for field in form_fields:
            if field['name'] in cl.list_editable:
                editing_fields[field['name']] = field

        config['editing_fields'] = editing_fields

        return config

    def get_fields_list(self, request, cl):
        list_display = cl.model_admin.get_list_display(request)
        exclude = cl.model_admin.exclude or tuple()
        fields_list = tuple(
            filter(lambda item: item not in exclude, list_display))
        return fields_list
