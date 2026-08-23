from django.contrib import admin

from .models import Client, PaymentTransaction


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "client_type", "owning_partner", "status")
    search_fields = ("name", "phone", "national_id")
    list_filter = ("client_type", "status")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "amount", "method", "status", "paid_at")
    search_fields = ("gateway_ref", "client__name")
    list_filter = ("method", "status")
