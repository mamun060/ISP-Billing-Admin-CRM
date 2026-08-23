from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import AccessTemplate, TemplateFieldAccess, RoleFieldAccess


class TemplateFieldAccessInline(TabularInline):
    model = TemplateFieldAccess
    extra = 0


@admin.register(AccessTemplate)
class AccessTemplateAdmin(ModelAdmin):
    list_display = ("name", "code", "created_at")
    inlines = [TemplateFieldAccessInline]


@admin.register(RoleFieldAccess)
class RoleFieldAccessAdmin(ModelAdmin):
    list_display = ("role", "form", "group", "field", "access")
    search_fields = ("role__name", "form__code")
