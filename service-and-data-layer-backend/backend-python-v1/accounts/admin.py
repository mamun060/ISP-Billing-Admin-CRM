from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Role, Permission, RolePermission, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("id", "login_identifier", "email", "is_staff", "is_superuser")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "phone", "email")
    ordering = ("id",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "scope_type")
    search_fields = ("name",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "module")
    search_fields = ("code", "module")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "permission")
    search_fields = ("role__name", "permission__code")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role")
    search_fields = ("user__username", "role__name")
