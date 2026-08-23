from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import Role, User, UserRole
from form_permissions.models import FormDefinition, FormFieldGroup, FormField, RoleFieldAccess
from form_permissions.serializers import DynamicFieldsModelSerializer
from partners.models import Partner
from billing.models import Client


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
