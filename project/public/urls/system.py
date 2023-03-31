from django.urls import path
from ..views import system

app_name = 'system'
urlpatterns = [
    path(
        'media/private/<int:content_type_id>/<int:object_id>/<slug:field_name>/<filename>',
        system.private_file_view,
        name='private_file',
    ),
]
