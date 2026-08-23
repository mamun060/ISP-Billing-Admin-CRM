from django.contrib import admin

from .models import AccessTemplate, TemplateFieldAccess, RoleFieldAccess


class TemplateFieldAccessInline(admin.TabularInline):
    model = TemplateFieldAccess
    extra = 0


@admin.register(AccessTemplate)
class AccessTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    inlines = [TemplateFieldAccessInline]


@admin.register(RoleFieldAccess)
class RoleFieldAccessAdmin(admin.ModelAdmin):
    list_display = ("role", "form", "group", "field", "access")
    search_fields = ("role__name", "form__code")
