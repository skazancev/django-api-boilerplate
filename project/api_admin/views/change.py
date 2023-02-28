from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import CRUDMixin
from ..utils import ModelDiffHelper, get_form_fields


class ChangeView(CRUDMixin, APIView):
    """
    Change an existing instance of this model.
    """
    serializer_class = None
    permission_classes = []

    def get_serializer_instance(self, request, obj):
        serializer = None

        if request.method == 'PATCH':
            serializer = self.serializer_class(
                instance=obj, data=request.data, partial=True)

        elif request.method == 'PUT':
            serializer = self.serializer_class(instance=obj, data=request.data)

        elif request.method == 'GET':
            serializer = self.serializer_class(instance=obj)

        return serializer

    def update(self, request, object_id, admin):
        # validate the reverse to field reference
        to_field = request.query_params.get(TO_FIELD_VAR)
        if to_field and not admin.to_field_allowed(request, to_field):
            return Response({'detail': 'The field %s cannot be referenced.' % to_field},
                            status=status.HTTP_400_BAD_REQUEST)
        obj = admin.get_object(request, unquote(object_id), to_field)

        opts = admin.model._meta
        helper = ModelDiffHelper(obj)

        # if the object doesn't exist respond with not found
        if obj is None:
            msg = _("%(name)s with ID “%(key)s” doesn't exist. Perhaps it was deleted?") % {
                'name': admin.model._meta.verbose_name,
                'key': unquote(object_id),
            }
            return Response({'detail': msg}, status=status.HTTP_404_NOT_FOUND)

        # test user change permission in this model.
        if not admin.has_change_permission(request, obj):
            raise PermissionDenied

        # initiate the serializer based on the request method
        serializer = self.get_serializer_instance(request, obj)

        # if the method is get return the change form fields dictionary
        if request.method == 'GET':
            data = {
                'config': self.get_config(request, admin, obj=obj),
                'fields': get_form_fields(serializer, change=True),
                'inlines': self.get_inlines(request, admin, obj=obj),
            }

            return Response(data, status=status.HTTP_200_OK)

        # update and log the changes to the object
        if serializer.is_valid():
            updated_object = serializer.save()

            if admin.is_inline:
                parent_model = admin.parent_model
                model_admin = admin.admin_site._registry.get(parent_model)
                changed_object = parent_model.objects.get(
                    **{updated_object._meta.verbose_name: updated_object})
            else:
                model_admin = admin
                changed_object = updated_object

            # log the change of  change
            model_admin.log_change(request, changed_object, [{'changed': {
                'name': str(updated_object._meta.verbose_name),
                'object': str(updated_object),
                'fields': helper.set_changed_model(updated_object).changed_fields
            }}])
            msg = _(
                f'The {opts.verbose_name} “{str(updated_object)}” was changed successfully.')
            return Response({'data': serializer.data, 'detail': msg}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, object_id, admin):
        return self.update(request, object_id, admin)

    def patch(self, request, object_id, admin):
        return self.update(request, object_id, admin)

    def get(self, request, object_id, admin):
        return self.update(request, object_id, admin)
