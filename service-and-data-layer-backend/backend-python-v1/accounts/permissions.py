from django.db.models import Q
from rest_framework.permissions import BasePermission

from partners.models import Area, Zone


class HasModulePermission(BasePermission):
    message = "You do not have the required permission for this module."

    def __init__(self, permission_code=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_code = permission_code

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        permission_code = self.permission_code or getattr(view, "required_permission_code", None)
        if not permission_code:
            return False

        return request.user.has_permission_code(permission_code)


class PartnerScopedPermission(BasePermission):
    message = "You are not allowed to access records outside your partner scope."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        user_roles = request.user.user_roles.select_related("role")
        if user_roles.filter(role__scope_type="system").exists():
            return True

        return bool(request.user.partner_id)

    def filter_queryset(self, request, queryset, view=None):
        if not request.user or not request.user.is_authenticated:
            return queryset.none()

        if request.user.user_roles.filter(role__scope_type="system").exists():
            return queryset

        partner = request.user.partner
        if not partner:
            return queryset.none()

        partner_ids = [partner.id]
        descendants = partner.get_descendants(include_self=True)
        partner_ids.extend(descendants.values_list("id", flat=True))

        if queryset.model.__name__ == "Zone":
            return queryset.filter(partner_id__in=partner_ids)

        if queryset.model.__name__ == "Area":
            zone_ids = Zone.objects.filter(partner_id__in=partner_ids).values_list("id", flat=True)
            return queryset.filter(zone_id__in=zone_ids)

        if hasattr(queryset.model, "partner"):
            return queryset.filter(partner_id__in=partner_ids)

        if hasattr(queryset.model, "zone"):
            zone_ids = Zone.objects.filter(partner_id__in=partner_ids).values_list("id", flat=True)
            return queryset.filter(zone_id__in=zone_ids)

        return queryset.filter(id__in=[])
