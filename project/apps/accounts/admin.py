from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.admin.sites import site as default_site

from apps.accounts.models import User, Group
from apps.bases.admin import BaseAdmin
from utils.simple_history import CustomSimpleHistoryAdmin


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


@admin.register(User)
class UserAdmin(CustomSimpleHistoryAdmin, DjangoUserAdmin, BaseAdmin):
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password', 'first_name', 'last_name', 'whatsapp_enabled')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_email_verified', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'is_superuser', 'is_staff', 'is_email_verified', 'created')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_email_verified', 'is_active', 'is_staff')
    ordering = ('-is_superuser', 'email')
    readonly_fields = ('last_login', 'created', 'whatsapp_enabled')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)


default_site.unregister(DjangoGroup)
admin.site.register(Group, GroupAdmin)
