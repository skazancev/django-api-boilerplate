from django.template.loader import render_to_string
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class TemplatePreviewView(APIView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        content = request.data.get('content')

        return Response({
            'content': render_to_string('emails/base.html', {'body': content, 'request': request}),
        })
