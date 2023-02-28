from rest_framework import serializers

from api.accounts.serializers import UserSerializer as BaseUserSerializer


class UserSerializer(BaseUserSerializer):
    group = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('group',)

    def get_group(self, obj):
        if obj.is_superuser:
            return 'Superuser'

        if group := obj.groups.first():
            return group.name

        return 'No group'
