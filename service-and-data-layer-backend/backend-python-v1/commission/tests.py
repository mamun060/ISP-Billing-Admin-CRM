from datetime import date
from decimal import Decimal

from django.test import TestCase

from billing.models import Client, PaymentTransaction
from commission.models import CommissionLedger
from commission.tasks import calculate_commission
from packages.models import Package
from partners.models import CommissionAgreement, Partner


class CommissionTaskTests(TestCase):
    def setUp(self):
        self.hq = Partner.objects.create(name="HQ", code="HQ", type="HQ")
        self.mid = Partner.objects.create(name="Mid Partner", code="MID", type="ZONE", parent=self.hq)
        self.leaf = Partner.objects.create(name="Leaf Partner", code="LEAF", type="AREA", parent=self.mid)

        self.package = Package.objects.create(
            name="Starter",
            type="internet",
            price=Decimal("100.00"),
            speed="10 Mbps",
            validity_days=30,
            status="active",
        )

        self.client = Client.objects.create(
            name="Example Client",
            phone="+123456789",
            client_type="residential",
            owning_partner=self.leaf,
            package=self.package,
            status="active",
        )

        CommissionAgreement.objects.create(
            partner=self.mid,
            parent=self.hq,
            pool_percentage=Decimal("60"),
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )
        CommissionAgreement.objects.create(
            partner=self.leaf,
            parent=self.mid,
            pool_percentage=Decimal("5"),
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )

    def test_calculate_commission_uses_100_60_5_35_example(self):
        transaction = PaymentTransaction.objects.create(
            client=self.client,
            package=self.package,
            amount=Decimal("100.00"),
            method="bkash",
            gateway_ref="TX-100-60-5-35",
            status="paid",
            paid_at=date(2025, 2, 1),
        )

        result = calculate_commission(transaction.id)

        self.assertEqual(len(result), 3)
        self.assertEqual(CommissionLedger.objects.filter(transaction=transaction).count(), 3)

        ledger_by_partner = {entry.partner_id: entry for entry in CommissionLedger.objects.filter(transaction=transaction)}
        self.assertEqual(ledger_by_partner[self.leaf.id].retained_percentage, Decimal("5"))
        self.assertEqual(ledger_by_partner[self.leaf.id].retained_amount, Decimal("5.00"))
        self.assertEqual(ledger_by_partner[self.mid.id].retained_percentage, Decimal("55"))
        self.assertEqual(ledger_by_partner[self.mid.id].retained_amount, Decimal("55.00"))
        self.assertEqual(ledger_by_partner[self.hq.id].retained_percentage, Decimal("40"))
        self.assertEqual(ledger_by_partner[self.hq.id].retained_amount, Decimal("40.00"))

    def test_calculate_commission_is_retry_safe(self):
        transaction = PaymentTransaction.objects.create(
            client=self.client,
            package=self.package,
            amount=Decimal("100.00"),
            method="bkash",
            gateway_ref="TX-RETRY",
            status="paid",
            paid_at=date(2025, 2, 1),
        )

        first = calculate_commission(transaction.id)
        second = calculate_commission(transaction.id)

        self.assertEqual(len(first), len(second))
        self.assertEqual(CommissionLedger.objects.filter(transaction=transaction).count(), 3)
