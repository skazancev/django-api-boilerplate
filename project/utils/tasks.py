import logging

from django.db.models import QuerySet

logger = logging.getLogger(__name__)


def get_object_with_logging(queryset, pk=None, **kwargs):
    if (not pk and not kwargs) or (pk and kwargs):
        raise ValueError(_('The only one of pk or kwargs is required'))

    lookup = kwargs or {'pk': pk}
    if not isinstance(queryset, QuerySet):
        queryset = queryset._meta.base_manager.all()

    obj = queryset.filter(**lookup).first()

    if obj is None:
        logger.exception(_(f'None object was returned for model "{queryset.model.__name__}" with params {lookup}'))

    return obj


class TaskError(Exception):
    pass
