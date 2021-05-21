from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers import ModelSerializer


class BaseInstanceSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f'{obj._meta.app_label}.{obj._meta.model_name}'


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'name', 'phone')
