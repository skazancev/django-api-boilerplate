from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import CRUDMixin
from ..utils import get_form_fields


class AddView(CRUDMixin, APIView):
    """
    Add new instances of this model.
    """
    serializer_class = None
    permission_classes = []

    def get(self, request, model_admin):
        data = dict()
        serializer = self.serializer_class()
        data['fields'] = get_form_fields(serializer)
        data['config'] = self.get_config(request, model_admin)

        if not model_admin.is_inline:
            data['inlines'] = self.get_inlines(request, model_admin)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, model_admin):
        # if the user doesn't have added permission respond with permission denied
        if not model_admin.has_add_permission(request):
            raise PermissionDenied

        # validate data and send
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            opts = model_admin.model._meta
            new_object = serializer.save()

            if model_admin.is_inline:
                parent_model = model_admin.parent_model
                change_object = parent_model.objects.get(
                    **{new_object._meta.verbose_name: new_object})
                model_admin = model_admin.admin_site._registry.get(
                    parent_model)
            else:
                model_admin = model_admin
                change_object = new_object

            # log addition of the new instance
            model_admin.log_addition(request, change_object, [{'added': {
                'name': str(new_object._meta.verbose_name),
                'object': str(new_object),
            }}])
            msg = _(
                f'The {opts.verbose_name} “{str(new_object)}” was added successfully.')
            return Response({'data': serializer.data, 'detail': msg}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
