from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Permission, Role, RolePermission


class Command(BaseCommand):
    help = "Create the initial CRM role and permission matrix for the admin, zone, and area portals."

    PERMISSION_DEFINITIONS = [
        {
            "code": "client.view",
            "module": "client",
            "description": "View client records.",
        },
        {
            "code": "client.manage",
            "module": "client",
            "description": "Create, update, and manage client records.",
        },
        {
            "code": "billing.view",
            "module": "billing",
            "description": "View billing information.",
        },
        {
            "code": "billing.manage",
            "module": "billing",
            "description": "Create, update, and manage billing entries.",
        },
        {
            "code": "commission.view",
            "module": "commission",
            "description": "View commission details and reports.",
        },
        {
            "code": "commission.manage",
            "module": "commission",
            "description": "Create, adjust, and reconcile commission data.",
        },
        {
            "code": "package.view",
            "module": "package",
            "description": "View the package catalog.",
        },
        {
            "code": "package.manage",
            "module": "package",
            "description": "Create, update, and manage packages.",
        },
    ]

    ROLE_SCOPE_DEFAULTS = {
        "Super Admin": "system",
        "Department Supervisor": "system",
        "Operation Team": "system",
        "Support Team": "system",
        "Core Team": "system",
        "Sales Team": "system",
        "Zone Admin": "zone",
        "Zone Team Member": "zone",
        "Area Admin": "area",
        "Area Team Member": "area",
        "Contact Center": "partner",
    }

    ROLE_PERMISSION_DEFAULTS = {
        "Super Admin": {
            "client.view",
            "client.manage",
            "billing.view",
            "billing.manage",
            "commission.view",
            "commission.manage",
            "package.view",
            "package.manage",
        },
        "Department Supervisor": {
            "client.view",
            "client.manage",
            "billing.view",
            "billing.manage",
            "commission.view",
            "commission.manage",
            "package.view",
            "package.manage",
        },
        "Operation Team": {
            "client.view",
            "client.manage",
            "billing.view",
            "billing.manage",
            "commission.view",
            "commission.manage",
            "package.view",
        },
        "Support Team": {
            "client.view",
            "billing.view",
            "commission.view",
            "package.view",
        },
        "Core Team": {
            "client.view",
            "client.manage",
            "billing.view",
            "billing.manage",
            "commission.view",
            "package.view",
        },
        "Sales Team": {
            "client.view",
            "client.manage",
            "commission.view",
            "commission.manage",
            "package.view",
        },
        "Zone Admin": {
            "client.view",
            "client.manage",
            "billing.view",
            "billing.manage",
            "commission.view",
            "commission.manage",
            "package.view",
        },
        "Zone Team Member": {
            "client.view",
            "billing.view",
            "commission.view",
            "package.view",
        },
        "Area Admin": {
            "client.view",
            "client.manage",
            "billing.view",
            "commission.view",
            "package.view",
        },
        "Area Team Member": {
            "client.view",
            "billing.view",
            "commission.view",
            "package.view",
        },
        "Contact Center": {
            "client.view",
            "client.manage",
            "billing.view",
            "commission.view",
            "package.view",
        },
    }

    def handle(self, *args, **options):
        with transaction.atomic():
            permission_map = {}
            for definition in self.PERMISSION_DEFINITIONS:
                permission, _ = Permission.objects.update_or_create(
                    code=definition["code"],
                    defaults={
                        "module": definition["module"],
                        "description": definition["description"],
                    },
                )
                permission_map[permission.code] = permission

            created_roles = []
            for role_name, scope_type in self.ROLE_SCOPE_DEFAULTS.items():
                role, created = Role.objects.update_or_create(
                    name=role_name,
                    defaults={"scope_type": scope_type},
                )
                created_roles.append(role)

                # Clear stale mappings before repopulating with defaults.
                role.permissions.all().delete()

                for permission_code in sorted(self.ROLE_PERMISSION_DEFAULTS.get(role_name, set())):
                    permission = permission_map.get(permission_code)
                    if permission is None:
                        continue
                    RolePermission.objects.update_or_create(
                        role=role,
                        permission=permission,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(self.ROLE_SCOPE_DEFAULTS)} roles and {len(self.PERMISSION_DEFINITIONS)} permissions."
            )
        )
