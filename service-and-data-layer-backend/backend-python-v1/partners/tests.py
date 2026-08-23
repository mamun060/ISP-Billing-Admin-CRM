from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from partners.models import CommissionAgreement, Partner


class CommissionAgreementTests(TestCase):
    def setUp(self):
        self.hq = Partner.objects.create(name="HQ", code="HQ-1", type="HQ")

    def test_valid_nested_agreement(self):
        parent = Partner.objects.create(name="Parent Partner", code="P-1", type="ZONE", parent=self.hq)
        child = Partner.objects.create(name="Child Partner", code="C-1", type="AREA", parent=parent)

        CommissionAgreement.objects.create(
            partner=parent,
            parent=self.hq,
            pool_percentage=60,
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )

        agreement = CommissionAgreement(
            partner=child,
            parent=parent,
            pool_percentage=30,
            effective_from=date(2025, 2, 1),
            effective_to=date(2025, 11, 30),
        )

        agreement.full_clean()
        agreement.save()

        self.assertEqual(agreement.pool_percentage, 30)

    def test_agreement_exceeding_parent_cap_raises(self):
        parent = Partner.objects.create(name="Parent Partner", code="P-2", type="ZONE", parent=self.hq)
        child = Partner.objects.create(name="Child Partner", code="C-2", type="AREA", parent=parent)

        CommissionAgreement.objects.create(
            partner=parent,
            parent=self.hq,
            pool_percentage=40,
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )

        agreement = CommissionAgreement(
            partner=child,
            parent=parent,
            pool_percentage=41,
            effective_from=date(2025, 2, 1),
            effective_to=date(2025, 11, 30),
        )

        with self.assertRaises(ValidationError):
            agreement.full_clean()

    def test_no_active_agreement_edge_case(self):
        parent = Partner.objects.create(name="Parent Partner", code="P-3", type="ZONE", parent=self.hq)
        child = Partner.objects.create(name="Child Partner", code="C-3", type="AREA", parent=parent)

        agreement = CommissionAgreement(
            partner=child,
            parent=parent,
            pool_percentage=25,
            effective_from=date(2025, 2, 1),
            effective_to=date(2025, 11, 30),
        )

        self.assertIsNone(CommissionAgreement.objects.get_active_agreement(parent, date(2025, 1, 5)))

        agreement.full_clean()
        agreement.save()
        self.assertIsNotNone(CommissionAgreement.objects.get_active_agreement(child, date(2025, 3, 1)))
