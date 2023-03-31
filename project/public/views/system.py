import mimetypes

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse


def private_file_view(request, content_type_id, object_id, field_name, filename):
    try:
        ctype = ContentType.objects.get_for_id(content_type_id)
        obj = ctype.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.user.is_superuser or obj.check_private_file_access(request, obj):
        file = getattr(obj, field_name)
        if file.filename == filename:
            response = HttpResponse(headers={
                'Content-Type': mimetypes.guess_type(file.real_url)[0],
            })
            response['X-Accel-Redirect'] = file.real_url
            return response
    raise PermissionDenied('You do not have permissions to view this file.')
