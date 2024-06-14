from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 

from api.apps.task.models import task

from django.utils.translation import gettext_lazy as _

# Personalizando a variável de custo dos conjuntos de campos
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = ( 
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
    
# Personalizando a página para alterar usuários.



admin.site.register(task.TaskProfile)
admin.site.register(task.TaskResponsible)
admin.site.register(task.User, UserAdmin)
