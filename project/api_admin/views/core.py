import json

from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.utils.translation import gettext_lazy as _
from django.views.i18n import JSONCatalog
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class IndexView(APIView):
    """
    Return json object that lists all the installed
    apps that have been registered by the admin site.
    """
    permission_classes = []

    def get(self, request, admin_site):
        app_list = admin_site.get_app_list(request)
        # add an url to app_index in every app in app_list
        for app in app_list:
            url = reverse(f'{admin_site.name}:app_list', kwargs={
                'app_label': app['app_label']}, request=request)
            app['url'] = url
        data = {
            'app_list': app_list,
        }
        request.current_app = admin_site.name
        return Response(data, status=status.HTTP_200_OK)


class AppIndexView(APIView):
    """
    Lists models inside a given app.
    """

    permission_classes = []

    def get(self, request, app_label, admin_site):
        app_dict = admin_site._build_app_dict(request, app_label)

        if not app_dict:
            return Response({'detail': _('The requested admin page does not exist.')},
                            status=status.HTTP_404_NOT_FOUND)

        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])

        data = {
            'app_label': app_label,
            'app': app_dict,
        }

        return Response(data, status=status.HTTP_200_OK)


class LanguageCatalogView(APIView):
    """
      Returns json object with django.contrib.admin i18n translation catalog
      to be used by a client site javascript library
    """
    permission_classes = []

    def get(self, request):
        response = JSONCatalog.as_view()(request)
        return Response(response.content, status=response.status_code)


class AutoCompleteView(APIView):
    """Handle AutocompleteWidget's AJAX requests for data."""
    permission_classes = []

    def get(self, request, admin_site):
        response = AutocompleteJsonView.as_view(admin_site=admin_site)(request)
        return Response({'content': response.content}, status=response.status_code)


class SiteContextView(APIView):
    """
    Returns the Attributes of AdminSite class (e.g. site_title, site_header)
    """
    permission_classes = []

    def get(self, request, admin_site):
        context = admin_site.each_context(request)
        return Response(context, status=status.HTTP_200_OK)


class AdminLogView(APIView):
    """
    Returns a list of actions that were preformed using django admin.
    """
    serializer_class = None
    pagination_class = None
    permission_classes = []
    ordering_fields = ['action_time', '-action_time']

    def get(self, request, admin_site):
        from django.contrib.admin.models import LogEntry

        queryset = LogEntry.objects.all()

        # order the queryset
        try:
            ordering = self.request.query_params.get('o')
            if ordering is not None:
                if ordering not in self.ordering_fields:
                    raise KeyError
                queryset = queryset.order_by(ordering)
        except Exception:
            return Response({'detail': 'Wrong ordering field set.'}, status=status.HTTP_400_BAD_REQUEST)

        # filter the queryset.
        try:
            object_id = self.request.query_params.get('object_id')
            if object_id is not None:
                queryset = queryset.filter(object_id=object_id)
        except Exception:
            return Response({'detail': 'Bad filters.'}, status=status.HTTP_400_BAD_REQUEST)

        # paginate queryset.
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        # serialize queryset.
        serializer = self.serializer_class(page, many=True)

        return Response({
            'action_list': self.serialize_messages(serializer.data),
            'config': self.get_config(page, queryset)},
            status=status.HTTP_200_OK)

    def serialize_messages(self, data):
        for idx, item in enumerate(data, start=0):
            data[idx]['change_message'] = json.loads(
                item['change_message'] or '[]')
        return data

    def get_config(self, page, queryset):
        return {
            'result_count': len(page),
            'full_result_count': queryset.count(),
        }


class AdminAPIRootView(APIView):
    """
    A list of all root urls in django_api_admin
    """
    root_urls = None

    def get(self, request, *args, **kwargs):
        namespace = request.resolver_match.namespace
        data = dict()

        for url in self.root_urls:
            if request.user.is_authenticated and url.name == 'login':
                continue
            elif not request.user.is_authenticated and url.name in ('logout', 'password_change'):
                continue
            data[url.name] = reverse(
                namespace + ':' + url.name, request=request, args=args, kwargs=kwargs)

        return Response(data or {}, status=status.HTTP_200_OK)
