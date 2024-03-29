from rest_framework import serializers


class SerializerUserMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'update_metadata'):
            self.instance.update_metadata(
                user=self._user if self._user and self._user.is_authenticated else None,
                history_change_reason=self._request.path if self._request else self.__class__.__name__,
            )

    @property
    def _request(self):
        return self.context.get('request')

    @property
    def _user(self):
        return getattr(self._request, 'user', None)

    def _absolute_uri(self, url):
        try:
            return self._request.build_absolute_uri(url)
        except AttributeError:
            return url


class Serializer(SerializerUserMixin,
                 serializers.Serializer):
    """Use it instead of rest_framework.Serializer"""
    pass


class ModelSerializer(SerializerUserMixin,
                      serializers.ModelSerializer):
    """Use it instead of rest_framework.ModelSerializer"""
    pass
