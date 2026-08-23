from typing import Iterable, Optional

from .models import FormDefinition, FormField, RoleFieldAccess


def _normalize_access(access: str) -> str:
    return access or RoleFieldAccess.ACCESS_HIDDEN


def resolve_field_access_for_role(role, form: FormDefinition, field_key: str) -> str:
    """Resolve access for a single role following specificity:
    1) RoleFieldAccess for specific field
    2) RoleFieldAccess for group
    3) Hidden
    Returns one of RoleFieldAccess.ACCESS_* strings.
    """
    try:
        field = FormField.objects.get(form=form, key=field_key)
    except FormField.DoesNotExist:
        return RoleFieldAccess.ACCESS_HIDDEN

    # field-level override
    rfa = RoleFieldAccess.objects.filter(role=role, form=form, field=field).first()
    if rfa:
        return _normalize_access(rfa.access)

    # group-level
    if field.group_id:
        rfa = RoleFieldAccess.objects.filter(role=role, form=form, group=field.group).first()
        if rfa:
            return _normalize_access(rfa.access)

    return RoleFieldAccess.ACCESS_HIDDEN


def resolve_field_access(roles: Iterable, form: FormDefinition, field_key: str) -> str:
    """Combine access across multiple roles, returning the most permissive access.
    Order: read_write > write > read > hidden
    """
    priority = [
        RoleFieldAccess.ACCESS_READ_WRITE,
        RoleFieldAccess.ACCESS_WRITE,
        RoleFieldAccess.ACCESS_READ,
        RoleFieldAccess.ACCESS_HIDDEN,
    ]

    highest = RoleFieldAccess.ACCESS_HIDDEN
    for role in roles:
        access = resolve_field_access_for_role(role, form, field_key)
        if priority.index(access) < priority.index(highest):
            # lower index = higher priority
            highest = access
            if highest == RoleFieldAccess.ACCESS_READ_WRITE:
                break

    return highest
