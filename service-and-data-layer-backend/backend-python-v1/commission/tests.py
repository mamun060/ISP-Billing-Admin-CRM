from datetime import date
from decimal import Decimal

from django.test import TestCase

from billing.models import Client, PaymentTransaction
from billing.services import record_payment
from commission.models import CommissionLedger
from commission.tasks import calculate_commission
from packages.models import Package
from partners.models import CommissionAgreement, Partner


class CommissionTaskTests(TestCase):
    def setUp(self):
        self.hq = Partner.objects.create(name="HQ", code="HQ", type="HQ")
        self.zone = Partner.objects.create(name="Zone Partner", code="ZONE", type="ZONE", parent=self.hq)
        self.area = Partner.objects.create(name="Area Partner", code="AREA", type="AREA", parent=self.zone)

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
            owning_partner=self.area,
            package=self.package,
            status="active",
        )

        CommissionAgreement.objects.create(
            partner=self.zone,
            parent=self.hq,
            pool_percentage=Decimal("40"),
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )
        CommissionAgreement.objects.create(
            partner=self.area,
            parent=self.zone,
            pool_percentage=Decimal("35"),
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )

    def test_calculate_commission_uses_hq_zone_area_60_5_35_example(self):
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
        self.assertEqual(ledger_by_partner[self.area.id].retained_percentage, Decimal("35"))
        self.assertEqual(ledger_by_partner[self.area.id].retained_amount, Decimal("35.00"))
        self.assertEqual(ledger_by_partner[self.zone.id].retained_percentage, Decimal("5"))
        self.assertEqual(ledger_by_partner[self.zone.id].retained_amount, Decimal("5.00"))
        self.assertEqual(ledger_by_partner[self.hq.id].retained_percentage, Decimal("60"))
        self.assertEqual(ledger_by_partner[self.hq.id].retained_amount, Decimal("60.00"))

    def test_record_payment_phase_1_flow_generates_expected_ledgers(self):
        transaction = record_payment(
            client_id=self.client.id,
            amount=Decimal("100.00"),
            method="bkash",
            gateway_ref="TX-PHASE-1-100",
        )

        calculate_commission(transaction.id)

        ledger_by_partner = {entry.partner_id: entry for entry in CommissionLedger.objects.filter(transaction=transaction)}
        self.assertEqual(ledger_by_partner[self.area.id].retained_percentage, Decimal("35"))
        self.assertEqual(ledger_by_partner[self.zone.id].retained_percentage, Decimal("5"))
        self.assertEqual(ledger_by_partner[self.hq.id].retained_percentage, Decimal("60"))

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
