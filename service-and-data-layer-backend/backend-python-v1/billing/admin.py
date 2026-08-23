from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Client, PaymentTransaction


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "full-width",
                    "placeholder": "Full name",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "full-width",
                    "placeholder": "01xxxxxxxxx",
                }
            ),
            "national_id": forms.TextInput(
                attrs={"class": "full-width"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "full-width"}
            ),
            "alternate_phone": forms.TextInput(
                attrs={"class": "full-width"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "full-width",
                    "rows": 3,
                }
            ),
            "division": forms.Select(
                attrs={"class": "full-width"}
            ),
            "district": forms.Select(
                attrs={"class": "full-width"}
            ),
            "upazila": forms.Select(
                attrs={"class": "full-width"}
            ),
            "owning_partner": forms.Select(
                attrs={"class": "full-width"}
            ),
            "package": forms.Select(
                attrs={"class": "full-width"}
            ),
        }


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    form = ClientForm

    class Media:
        css = {
            "all": ("admin/css/client_form.css",)
        }

    list_display = (
        "id",
        "name",
        "phone",
        "client_type",
        "owning_partner",
        "status",
    )

    search_fields = (
        "name",
        "phone",
        "national_id",
    )

    list_filter = (
        "client_type",
        "status",
    )

    fieldsets = (
        (
            "Client profile",
            {
                "fields": (
                    ("name", "phone"),
                    ("client_type", "status"),
                ),
                "description": "Enter the client’s primary contact details and account status.",
            },
        ),
        (
            "Service & ownership",
            {
                "fields": (("owning_partner", "package"),),
                "description": "Assign the client to the responsible partner and service package.",
            },
        ),
        (
            "Contact & identity",
            {
                "fields": (
                    ("email", "alternate_phone"),
                    ("national_id", "date_of_birth"),
                    "gender",
                    "address",
                ),
                "description": "Optional personal details used for communication and verification.",
            },
        ),
        (
            "Location",
            {
                "fields": (
                    ("division", "district"),
                    ("upazila", "union"),
                ),
                "description": "Select the client’s service location from broadest to most specific.",
            },
        ),
        (
            "Verification documents",
            {
                "fields": (("image", "nid_scan"),),
                "classes": ("collapse",),
                "description": "Upload supporting files when they are available.",
            },
        ),
    )


class PaymentTransactionForm(forms.ModelForm):
    class Meta:
        model = PaymentTransaction
        fields = "__all__"
        widgets = {
            "client": forms.Select(attrs={"class": "vSelect full-width"}),
            "package": forms.Select(attrs={"class": "vSelect full-width"}),
            "amount": forms.NumberInput(attrs={"class": "vTextField full-width"}),
            "method": forms.Select(attrs={"class": "vSelect full-width"}),
            "gateway_ref": forms.TextInput(attrs={"class": "vTextField full-width"}),
            "paid_at": forms.DateInput(attrs={"type": "date", "class": "vTextField"}),
        }


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    form = PaymentTransactionForm
    list_display = ("id", "client", "amount", "method", "status", "paid_at")
    search_fields = ("gateway_ref", "client__name")
    list_filter = ("method", "status")
    fieldsets = (
        (None, {'fields': ('client', 'package', 'amount', 'method', 'gateway_ref')}),
        ('Status', {'fields': ('status', 'paid_at')}),
    )
