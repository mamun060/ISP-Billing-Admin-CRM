from decimal import Decimal

from django.db import models

from billing.models import PaymentTransaction
from partners.models import CommissionAgreement, Partner


class CommissionLedger(models.Model):
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name="commission_ledger")
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="commission_ledgers")
    retained_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    retained_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "commission_ledger"
        unique_together = ("transaction", "partner")

    def __str__(self):
        return f"{self.partner.name} - {self.retained_amount}"
