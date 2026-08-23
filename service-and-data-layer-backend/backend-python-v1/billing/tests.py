from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from packages.models import Package
from partners.models import Partner
from billing.models import Client, PaymentTransaction
from billing.services import record_payment


class BillingPaymentTests(TestCase):
    def setUp(self):
        self.hq = Partner.objects.create(name="HQ", code="HQ-1", type="HQ")
        self.package = Package.objects.create(
            name="Gold 50",
            type="internet",
            price=Decimal("1000.00"),
            speed="50 Mbps",
            validity_days=30,
            status="active",
        )
        self.client = Client.objects.create(
            name="Test Client",
            phone="+123456789",
            client_type="residential",
            owning_partner=self.hq,
            package=self.package,
            status="active",
        )

    def test_record_payment_creates_transaction_and_enqueues_commission(self):
        payment = record_payment(
            client_id=self.client.id,
            amount=Decimal("1000.00"),
            method="bkash",
            gateway_ref="GW-001",
        )

        self.assertEqual(payment.status, "paid")
        self.assertTrue(PaymentTransaction.objects.filter(gateway_ref="GW-001").exists())

    def test_record_payment_rejects_duplicate_gateway_ref(self):
        record_payment(
            client_id=self.client.id,
            amount=Decimal("1000.00"),
            method="bkash",
            gateway_ref="GW-002",
        )

        with self.assertRaises(ValueError):
            record_payment(
                client_id=self.client.id,
                amount=Decimal("2500.00"),
                method="nagad",
                gateway_ref="GW-002",
            )
