from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from packages.models import Package
from partners.models import Partner


class Client(models.Model):
    CLIENT_TYPES = (
        ("residential", "Residential"),
        ("business", "Business"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
    )

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    client_type = models.CharField(max_length=30, choices=CLIENT_TYPES, default="residential")
    owning_partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="clients")
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="clients")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_client"

    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    METHOD_CHOICES = (
        ("cash", "Cash"),
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
        ("bank", "Bank Transfer"),
        ("card", "Card"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="payments")
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    gateway_ref = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_payment_transaction"

    def __str__(self):
        return f"{self.client.name} - {self.amount}"
