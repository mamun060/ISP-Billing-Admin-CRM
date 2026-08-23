from django.contrib import admin

from .models import CommissionLedger


@admin.register(CommissionLedger)
class CommissionLedgerAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "partner", "retained_amount", "created_at")
    search_fields = ("transaction__gateway_ref", "partner__name")
