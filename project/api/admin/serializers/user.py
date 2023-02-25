from rest_framework import serializers

from api.accounts.serializers import UserSerializer


class AdminUserSerializer(UserSerializer):
    group = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('group',)

    def get_group(self, obj):
        if obj.is_superuser:
            return 'Superuser'

        if group := obj.groups.first():
            return group.name

        return 'No group'
