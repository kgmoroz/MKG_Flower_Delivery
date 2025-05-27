from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(DefaultUserAdmin):
    # здесь можно дополнительно настроить отображаемые столбцы
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('phone', 'address'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'address', 'is_staff')