from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm    # та, что вы создавали
CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для кастомного пользователя без поля usable_password."""

    # ----- формы -----------------------------------------------------------
    add_form = CustomUserCreationForm
    model     = CustomUser

    # ----- список ----------------------------------------------------------
    list_display = ("username", "email", "phone", "is_staff", "is_active")
    list_filter  = ("is_staff", "is_active", "groups")

    # ----- поля при редактировании ----------------------------------------
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональные данные", {"fields": ("first_name", "last_name", "email", "phone", "address")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    # ----- поля при создании пользователя ----------------------------------
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email",
                "first_name", "last_name",
                "phone", "address",
                "password1", "password2",
                "is_staff", "is_active",
            ),
        }),
    )

    search_fields = ("username", "email", "phone")
    ordering      = ("username",)
