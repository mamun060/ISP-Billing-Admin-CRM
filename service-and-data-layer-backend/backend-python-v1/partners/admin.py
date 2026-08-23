from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Partner, CommissionAgreement, Zone, Area, Division, District, Upazila, Union


@admin.register(Partner)
class PartnerAdmin(MPTTModelAdmin):
    list_display = ("id", "name", "code", "type", "parent")
    search_fields = ("name", "code")


@admin.register(CommissionAgreement)
class CommissionAgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "partner", "parent", "pool_percentage", "effective_from", "effective_to")
    list_filter = ("effective_from",)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "partner")
    search_fields = ("name",)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "zone")
    search_fields = ("name",)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "division", "code")


@admin.register(Upazila)
class UpazilaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "district", "code")


@admin.register(Union)
class UnionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "upazila", "code")
