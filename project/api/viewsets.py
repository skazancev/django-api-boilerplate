from typing import Optional

from django.conf import settings
from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet as BaseGenericViewSet

from api.serializers import Serializer


class BrowsableAPIRendererQuerySetFix(object):
    def get_queryset(self):
        try:
            # noinspection PyUnresolvedReferences
            return super().get_queryset()

        except AssertionError:
            if any(x.endswith('BrowsableAPIRenderer') for x in settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']):
                return QuerySet().none()

            raise


class GenericViewSet(BrowsableAPIRendererQuerySetFix, BaseGenericViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = 'uid'
    serializer_class = Serializer

    def get_object(self):
        obj = super().get_object()
        if obj and hasattr(obj, 'update_metadata'):
            obj.update_metadata(
                user=self.request.user,
                history_change_reason=self.request.path if self.request else self.__class__.__name__,
            )
        return obj

    @property
    def method(self):
        if self.action is not None:
            return getattr(self, self.action, None)

    def get_permissions(self):
        permissions = getattr(self.method, 'extra_permissions', [])
        assert isinstance(permissions, list)

        return [permission() for permission in [*self.permission_classes, *permissions]]

    def get_serializer_class(self, validator=False):
        try:
            return getattr(self.method, 'validator_class' if validator else 'serializer_class')
        except AttributeError:
            return super().get_serializer_class()

    def get_serializer(self, *args, validator=False, **kwargs) -> Optional[Serializer]:
        _serializer = kwargs.pop('serializer_class', None)
        if _serializer is None:
            _serializer = self.get_serializer_class(validator=validator)

        kwargs['context'] = dict(
            **(kwargs.get('context') or {}),
            **self.get_serializer_context(),
        )

        if _serializer:
            return _serializer(*args, **kwargs)

    def get_validation_serializer(self, *args, **kwargs):
        return self.get_serializer(*args, validator=True, **kwargs)

    def validate_request(self, request, *args, **kwargs):
        if isinstance(request, Request):
            if request.method == 'GET':
                data = request.GET.dict().copy()
            else:
                data = request.data
        else:
            data = request

        _serializer = self.get_validation_serializer(data=data, *args, **kwargs)
        _serializer.is_valid(raise_exception=True)

        return _serializer

    def response(self, instance=None, *args, directly=True, **kwargs):
        if instance is not None:
            if directly and isinstance(instance, (list, dict, tuple)):
                kwargs.setdefault('data', instance)
            else:
                _serializer = self.get_serializer(
                    instance,
                    serializer_class=kwargs.pop('serializer_class', None),
                    context=kwargs.pop('context', None),
                )
                kwargs.setdefault('data', _serializer.data)

        return Response(**kwargs)

    def response_list(self, instance, *args, **kwargs):
        _serializer = self.get_serializer(
            instance,
            many=True,
            serializer_class=kwargs.pop('serializer_class', None),
            context=kwargs.pop('context', None),
        )

        return Response(data=_serializer.data, **kwargs)

    def paginated_response_list(self, queryset, *args, **kwargs):
        page = self.paginate_queryset(queryset)
        if page is not None:
            _serializer = self.get_serializer(page, many=True, serializer_class=kwargs.pop('serializer_class', None))
            return self.get_paginated_response(_serializer.data)

        _serializer = self.get_serializer(queryset, many=True, serializer_class=kwargs.pop('serializer_class', None))
        return Response(_serializer.data)

    def response_ok(self, **kwargs):
        return Response({'status': 'ok'}, **kwargs)

    def response_error(self, error_message: str, **kwargs):
        kwargs.setdefault('status', 400)
        return Response({api_settings.NON_FIELD_ERRORS_KEY: [error_message]}, **kwargs)

    def filter_queryset(self, queryset):
        if hasattr(self, 'filter_class'):
            return self.filter_class(self.request.GET, queryset, request=self.request).qs

        return queryset

    def get_authenticators(self) -> list:
        authenticators: list = super().get_authenticators()
        if getattr(self.request, 'is_internal', False):
            authenticators.append(SessionAuthentication())

        return authenticators


class serializer:
    def __init__(self,
                 klass,
                 *,
                 validator=None,
                 viewset=None,
                 swagger_schema=None,
                 skip_swagger=False,
                 response_status=status.HTTP_200_OK,
                 swagger_serializer_kwargs=None):
        self.viewset = viewset
        self.klass = klass
        self.validator = validator or klass
        self.swagger_schema = swagger_schema or dict()
        self.swagger_serializer_kwargs = swagger_serializer_kwargs or dict()
        self.response_status = response_status
        self.skip_swagger = skip_swagger

    _default_methods_mapping = {
        'list': ['get'],
        'create': ['post'],
        'update': ['put', 'patch'],
        'destroy': ['delete'],
        'retrieve': ['get'],
    }

    def __call__(self, func):
        mapping = getattr(func, 'mapping', None)
        if mapping is None:
            mapping = self._default_methods_mapping[func.__name__]

        if not self.skip_swagger:
            if set(mapping) & {'put', 'patch', 'post', 'delete'}:
                self.swagger_schema.setdefault('request_body', self.validator(**self.swagger_serializer_kwargs))

            self.swagger_schema.setdefault('responses', {
                self.response_status: self.klass(**self.swagger_serializer_kwargs)
            })

            func = swagger_auto_schema(**self.swagger_schema)(func)

        func.serializer_class = self.klass
        func.validator_class = self.validator

        return func

    def check_viewset(self):
        if self.viewset is None:
            raise ValueError('`viewset` property is required when `serializer()` is used as a context')

        if not isinstance(self.viewset, BaseGenericViewSet):
            raise ValueError('`viewset` should be an instance of `GenericViewSet` object')


def extra_permissions(permission_classes):
    def decorator(func):
        func.extra_permissions = permission_classes

        return func

    return decorator


def swagger_queryset_error(queryset):
    def decorator(get_queryset):
        def _wrap(self):
            try:
                return get_queryset(self)
            except Exception:
                if settings.SHOW_SWAGGER and self.request.resolver_match.func.__name__ == 'SchemaView':
                    return queryset
                raise
        return _wrap
    return decorator
