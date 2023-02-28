from django.contrib.admin.options import (TO_FIELD_VAR)
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class DetailView(APIView):
    """
    GET one instance of this model using pk and to_fields.
    """
    permission_classes = []
    serializer_class = None

    def get(self, request, object_id, admin):
        # validate the reverse to field reference
        to_field = request.query_params.get(TO_FIELD_VAR)
        if to_field and not admin.to_field_allowed(request, to_field):
            return Response({'detail': 'The field %s cannot be referenced.' % to_field},
                            status=status.HTTP_400_BAD_REQUEST)
        obj = admin.get_object(request, unquote(object_id), to_field)

        # if the object doesn't exist respond with not found
        if obj is None:
            msg = _("%(name)s with ID “%(key)s” doesn't exist. Perhaps it was deleted?") % {
                'name': admin.model._meta.verbose_name,
                'key': unquote(object_id),
            }
            return Response({'detail': msg}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(obj, context={'request': request})
        data = serializer.data

        info = (
            admin.admin_site.name,
            admin.model._meta.app_label,
            admin.model._meta.model_name,
        )
        pattern = '%s:%s_%s_'
        data['history_url'] = reverse(
            (pattern + 'history') % info,
            kwargs={'object_id': data['pk']},
            request=request,
        )
        if admin.view_on_site:
            model_type = ContentType.objects.get_for_model(model=admin.model)
            data['view_on_site'] = reverse(
                '%s:view_on_site' % admin.admin_site.name,
                kwargs={
                    'content_type_id': model_type.pk,
                    'object_id': obj.pk,
                },
                request=request
            )

        data['list_url'] = reverse((pattern + 'list') % info, request=request)
        data['delete_url'] = reverse(
            (pattern + 'delete') % info, kwargs={'object_id': data['pk']}, request=request)
        data['change_url'] = reverse(
            (pattern + 'change') % info, kwargs={'object_id': data['pk']}, request=request)
        return Response(data, status=status.HTTP_200_OK)
