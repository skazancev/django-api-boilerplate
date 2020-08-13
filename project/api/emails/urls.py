from django.urls import path

from api.emails.viewsets import TemplatePreviewView

app_name = 'emails'

urlpatterns = [
    path('templates/preview/', TemplatePreviewView.as_view(), name='templates-preview')
]
