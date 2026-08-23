from django.contrib import admin

from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "price", "status")
    search_fields = ("name",)
