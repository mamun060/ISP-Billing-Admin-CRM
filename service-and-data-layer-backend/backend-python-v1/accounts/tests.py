from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import Permission, Role, RolePermission, UserRole
from accounts.permissions import HasModulePermission, PartnerScopedPermission
from partners.models import Area, Partner, Zone

User = get_user_model()


class AccountsRBACBasicsTest(TestCase):
    def setUp(self):
        self.root_partner = Partner.objects.create(name="Root Partner", code="ROOT")
        self.child_partner = Partner.objects.create(name="Child Partner", code="CHILD", parent=self.root_partner)
        self.zone = Zone.objects.create(name="Test Zone", partner=self.child_partner)
        self.area = Area.objects.create(name="Test Area", zone=self.zone)

        self.role = Role.objects.create(name="Manager", scope_type="partner")
        self.permission = Permission.objects.create(code="view.billing", module="billing", description="View billing")
        RolePermission.objects.create(role=self.role, permission=self.permission)

        self.user = User.objects.create_user(
            phone="+1234567890",
            email="user@example.com",
            password="secret123",
            partner=self.child_partner,
        )
        UserRole.objects.create(user=self.user, role=self.role)

    def test_user_authentication_accepts_phone_or_email(self):
        self.assertIsNotNone(User.objects.create_user(phone="+111", email="login@example.com", password="pass123"))
        self.assertTrue(self.user.check_password("secret123"))

    def test_has_module_permission_checks_permission_code(self):
        request = APIRequestFactory().get("/api/test/")
        request.user = self.user

        permission = HasModulePermission(permission_code="view.billing")
        self.assertTrue(permission.has_permission(request, None))

    def test_partner_scoped_permission_filters_queryset(self):
        request = APIRequestFactory().get("/api/areas/")
        request.user = self.user

        permission = PartnerScopedPermission()
        queryset = Area.objects.all()
        filtered = permission.filter_queryset(request, queryset, None)

        self.assertIn(self.area, filtered)
        self.assertEqual(filtered.count(), 1)
