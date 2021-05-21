from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.admin.sites import site as default_site

from apps.accounts.models import User, Group
from apps.bases.admin import BaseAdmin
from utils.simple_history import CustomSimpleHistoryAdmin


class UserChangeForm(BaseUserChangeForm):
    password_reset_request = ReadOnlyPasswordHashField()


@admin.register(User)
class UserAdmin(CustomSimpleHistoryAdmin, DjangoUserAdmin, BaseAdmin):
    form = UserChangeForm
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_email_verified', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'is_superuser', 'is_staff', 'is_email_verified', 'created')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_email_verified', 'is_active', 'is_staff')
    ordering = ('-is_superuser', 'email')
    readonly_fields = ('last_login', 'created')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)


default_site.unregister(DjangoGroup)
admin.site.register(Group, GroupAdmin)
