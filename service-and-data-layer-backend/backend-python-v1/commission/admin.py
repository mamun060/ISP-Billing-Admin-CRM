from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CommissionLedger


@admin.register(CommissionLedger)
class CommissionLedgerAdmin(ModelAdmin):
    list_display = ("id", "transaction", "partner", "retained_amount", "created_at")
    search_fields = ("transaction__gateway_ref", "partner__name")
