from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Package


@admin.register(Package)
class PackageAdmin(ModelAdmin):
    list_display = ("id", "name", "type", "price", "status")
    search_fields = ("name",)
