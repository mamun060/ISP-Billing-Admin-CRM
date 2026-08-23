from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.module_loading import import_string

from .models import FormDefinition, RoleFieldAccess
from .services import resolve_field_access


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """Filters serializer fields on init (read) and enforces write permissions on input payloads.

    Expects a FormDefinition with code '<app_label>.<ModelName>' to exist, and FormField entries
    with keys matching serializer field names.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        user = getattr(request, "user", None)

        # determine roles
        roles = []
        if user and hasattr(user, "roles"):
            roles = [ur.role for ur in user.roles]

        # find form definition by model
        model = getattr(self.Meta, "model", None)
        self._form_def = None
        if model:
            code = f"{model._meta.app_label}.{model.__name__}"
            try:
                self._form_def = FormDefinition.objects.get(code=code)
            except FormDefinition.DoesNotExist:
                self._form_def = None

        # filter fields for read access
        if self._form_def and roles:
            allowed = set()
            for fname in list(self.fields.keys()):
                access = resolve_field_access(roles, self._form_def, fname)
                if access in (RoleFieldAccess.ACCESS_READ, RoleFieldAccess.ACCESS_READ_WRITE, RoleFieldAccess.ACCESS_WRITE):
                    # any of read/write/read_write allow the field to be present for read
                    allowed.add(fname)

            for fname in list(self.fields.keys()):
                if fname not in allowed:
                    self.fields.pop(fname)
        else:
            # no config -> hide all fields
            for fname in list(self.fields.keys()):
                self.fields.pop(fname)

    def to_internal_value(self, data):
        # enforce write permissions: user must have write or read_write for any provided write field
        request = self.context.get("request")
        user = getattr(request, "user", None)
        roles = []
        if user and hasattr(user, "roles"):
            roles = [ur.role for ur in user.roles]

        # If no form definition, no writes allowed
        if not self._form_def:
            raise ValidationError({"non_field_errors": ["No form permissions configured; writes are not allowed."]})

        # check each key in incoming data
        for key in getattr(data, "keys", lambda: data.keys())():
            # skip non-field keys
            if key not in self.fields:
                # if the incoming payload tries to set a field that was hidden, reject explicitly
                # check whether field exists in form definition
                # and if so, ensure user has write permission
                access = resolve_field_access(roles, self._form_def, key)
                if access not in (RoleFieldAccess.ACCESS_WRITE, RoleFieldAccess.ACCESS_READ_WRITE):
                    raise ValidationError({key: ["You do not have permission to modify this field."]})

        return super().to_internal_value(data)

    def _roles_have_reveal(self, roles):
        # check whether any role has module-level permission code 'reveal_sensitive'
        for role in roles:
            if role.permissions.filter(permission__code="reveal_sensitive").exists():
                return True
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # masking rule: bank_account -> show last 4 digits unless role has reveal_sensitive
        request = self.context.get("request")
        user = getattr(request, "user", None)
        roles = []
        if user and hasattr(user, "roles"):
            roles = [ur.role for ur in user.roles]

        if "bank_account" in data:
            reveal = self._roles_have_reveal(roles)
            val = data.get("bank_account")
            if val and not reveal:
                # mask all but last 4
                masked = "*" * max(0, len(val) - 4) + val[-4:]
                data["bank_account"] = masked

        return data
