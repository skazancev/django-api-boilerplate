from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ListView(APIView):
    """
    Return a list containing all instances of this model.
    """

    serializer_class = None
    permission_classes = []

    def get(self, request, admin):
        queryset = admin.get_queryset(request)
        page = admin.admin_site.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(page, many=True)
        data = serializer.data

        if admin.is_inline:
            info = (
                admin.admin_site.name, admin.parent_model._meta.app_label,
                admin.parent_model._meta.model_name, admin.opts.app_label,
                admin.opts.model_name
            )
            pattern = '%s:%s_%s_%s_%s_detail'
        else:
            info = (
                admin.admin_site.name,
                admin.model._meta.app_label,
                admin.model._meta.model_name
            )
            pattern = '%s:%s_%s_detail'

        for item in data:
            item['detail_url'] = reverse(pattern % info, kwargs={
                'object_id': int(item['pk'])}, request=request)
        return Response(data, status=status.HTTP_200_OK)
