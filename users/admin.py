from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import UserCreateForm, UserUpdateForm


class CustomUserAdmin(UserAdmin):
    add_form = UserCreateForm
    form = UserUpdateForm
    model = CustomUser

    list_display = ('username', 'origin_password', 'email', 'first_name', 'last_name', 'is_staff')

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ('username', 'first_name', 'last_name', 'email', 'password', 'profile_picture'),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("username", "password", "origin_password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "profile_picture", "friends")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
