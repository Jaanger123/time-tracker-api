from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import *


class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('email', 'is_staff', 'is_active', 'is_superuser')
    readonly_fields = ('activation_code', 'date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 
            'last_name', 
            'date_joined',  
            'date_left', 
            'country',
            'activation_code',
        )}),
        (_('Position info'), {'fields': ('position', 'grade')}),
        (_('Department info'), {'fields': ('department', 'department_role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name', 
                'password1', 
                'password2', 
                'position', 
                'grade', 
                'department',
                'department_role',
                'country',
                'is_active', 
                'is_staff', 
                'is_superuser',
            ),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(Position)
admin.site.register(Grade)
admin.site.register(Department)
admin.site.register(DepartmentRole)
admin.site.register(Country)