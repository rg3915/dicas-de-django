# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AuditEntry, Document, Profile, User


class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_active')  # noqa E501
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_admin',
                # 'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'birthday', 'linkedin', 'rg', 'cpf')
    search_fields = (
        'customer__first_name',
        'customer__last_name',
        'customer__email',
        'linkedin',
        'rg',
        'cpf'
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ('action', 'email', 'ip', 'created')
    list_filter = ('action',)


admin.site.register(User, UserAdmin)
