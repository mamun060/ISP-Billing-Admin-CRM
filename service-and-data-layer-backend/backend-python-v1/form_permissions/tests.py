from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import Role, User, UserRole, Permission, RolePermission
from form_permissions.models import FormDefinition, FormFieldGroup, FormField, RoleFieldAccess
from form_permissions.serializers import DynamicFieldsModelSerializer
from partners.models import Partner
from billing.models import Client
from partners.models import Zone


class DummyClientSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "phone", "national_id", "email", "address"]


class FormPermissionsTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.role = Role.objects.create(name="test-role")
        self.user = User.objects.create_user(phone="019000", username="u1", password="pass")
        UserRole.objects.create(user=self.user, role=self.role)

        # create form definition for Client
        self.form = FormDefinition.objects.create(code="billing.Client", name="Client Form")
        group = FormFieldGroup.objects.create(form=self.form, name="identity")
        self.field_nid = FormField.objects.create(form=self.form, group=group, name="National ID", key="national_id")
        self.field_email = FormField.objects.create(form=self.form, group=group, name="Email", key="email")

    def test_field_level_override_beats_group_default(self):
        # group default = read, but field-level override on national_id = write
        RoleFieldAccess.objects.create(role=self.role, form=self.form, group=self.field_nid.group, access=RoleFieldAccess.ACCESS_READ)
        RoleFieldAccess.objects.create(role=self.role, form=self.form, field=self.field_nid, access=RoleFieldAccess.ACCESS_WRITE)

        req = self.factory.get("/")
        req.user = self.user
        serializer = DummyClientSerializer(context={"request": req})
        # national_id should be present because group read + field override
        self.assertIn("national_id", serializer.fields)

    def test_missing_config_defaults_hidden(self):
        # remove form definition fields to simulate missing config
        FormField.objects.all().delete()
        req = self.factory.get("/")
        req.user = self.user
        serializer = DummyClientSerializer(context={"request": req})
        # no fields should be present
        self.assertEqual(len(serializer.fields), 0)

    def test_write_attempt_to_hidden_field_rejected(self):
        # no explicit access configured -> hidden
        req = self.factory.post("/", {"national_id": "12345"}, format="json")
        req.user = self.user
        serializer = DummyClientSerializer(data={"national_id": "12345"}, context={"request": req})
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)

    def test_masking_of_bank_account_without_reveal_permission(self):
        # create a zone and set bank account
        zone = Zone.objects.create(name="Z1", partner=Partner.objects.create(name="P", code="P1", type="HQ"))
        zone.set_bank_account("123456789012")
        zone.save()

        # create form definition and field for partners.Zone.bank_account
        form = FormDefinition.objects.create(code="partners.Zone", name="Zone Form")
        field = FormField.objects.create(form=form, name="Bank Account", key="bank_account")
        # grant role read access
        RoleFieldAccess.objects.create(role=self.role, form=form, field=field, access=RoleFieldAccess.ACCESS_READ)

        req = self.factory.get("/")
        req.user = self.user
        # use Zone serializer
        from partners.serializers import ZoneSerializer

        serializer = ZoneSerializer(zone, context={"request": req})
        data = serializer.data
        self.assertIn("bank_account", data)
        # should be masked (last 4 only)
        self.assertTrue(data["bank_account"].endswith("9012"))
        self.assertTrue(data["bank_account"].startswith("*") )

    def test_reveal_sensitive_permission_shows_full_account(self):
        # give role reveal_sensitive permission
        perm = Permission.objects.create(code="reveal_sensitive", module="security")
        RolePermission.objects.create(role=self.role, permission=perm)
        # ensure form and field exist (tests may have deleted them)
        form, _ = FormDefinition.objects.get_or_create(code="partners.Zone", defaults={"name": "Zone Form"})
        field, _ = FormField.objects.get_or_create(form=form, key="bank_account", defaults={"name": "Bank Account"})
        RoleFieldAccess.objects.get_or_create(role=self.role, form=form, field=field, defaults={"access": RoleFieldAccess.ACCESS_READ})

        # create a new zone to test
        zone = Zone.objects.create(name="Z3", partner=Partner.objects.create(name="P3", code="P3", type="HQ"))
        zone.set_bank_account("555566667777")
        zone.save()
        req = self.factory.get("/")
        req.user = self.user
        from partners.serializers import ZoneSerializer
        serializer = ZoneSerializer(zone, context={"request": req})
        data = serializer.data
        # now should show full (not masked)
        self.assertEqual(data["bank_account"], zone.get_bank_account())
