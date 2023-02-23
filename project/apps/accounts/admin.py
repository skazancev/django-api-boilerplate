from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.admin.sites import site as default_site
from django import forms

from apps.accounts.models import User, Group
from apps.bases.admin import BaseAdmin
from utils.simple_history import CustomSimpleHistoryAdmin


class UserCreationForm(BaseUserCreationForm):
    field = forms.CharField(
        required=False,
        initial='Hello!'
    )

    class Meta:
        model = User
        fields = ('email',)


@admin.register(User)
class UserAdmin(CustomSimpleHistoryAdmin, DjangoUserAdmin, BaseAdmin):
    add_form = UserCreationForm
    fieldsets = (
        (None, {
            'fields': ('email', 'phone', 'password', 'first_name', 'last_name', 'whatsapp_enabled')
        }),
        (_('Permissions'), {
            "classes": ("wide",),
            'fields': ('is_active', 'is_staff', 'is_email_verified', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'created'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'field'),
        }),
    )

    list_display = ('email', 'is_superuser', 'is_staff', 'is_email_verified', 'created')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_email_verified', 'is_active', 'is_staff')
    ordering = ('-is_superuser', 'email')
    readonly_fields = ('password', 'last_login', 'created', 'whatsapp_enabled', 'custom_field')

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)


default_site.unregister(DjangoGroup)
admin.site.register(Group, GroupAdmin)
