from django.db import models


class FormDefinition(models.Model):
    code = models.CharField(max_length=255, unique=True)  # e.g. "billing.Client"
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "form_permissions_formdefinition"

    def __str__(self):
        return self.code


class FormFieldGroup(models.Model):
    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "form_permissions_formfieldgroup"

    def __str__(self):
        return f"{self.form.code}::{self.name}"


class FormField(models.Model):
    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE, related_name="fields")
    group = models.ForeignKey(FormFieldGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="fields")
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)  # serializer/field key
    field_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "form_permissions_formfield"
        unique_together = ("form", "key")

    def __str__(self):
        return f"{self.form.code}:{self.key}"


class RoleFieldAccess(models.Model):
    ACCESS_HIDDEN = "hidden"
    ACCESS_READ = "read"
    ACCESS_WRITE = "write"
    ACCESS_READ_WRITE = "read_write"

    ACCESS_CHOICES = (
        (ACCESS_HIDDEN, "Hidden"),
        (ACCESS_READ, "Read"),
        (ACCESS_WRITE, "Write"),
        (ACCESS_READ_WRITE, "Read/Write"),
    )

    role = models.ForeignKey("accounts.Role", on_delete=models.CASCADE, related_name="field_accesses")
    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE, related_name="role_accesses")
    group = models.ForeignKey(FormFieldGroup, on_delete=models.CASCADE, null=True, blank=True)
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, null=True, blank=True)
    access = models.CharField(max_length=20, choices=ACCESS_CHOICES, default=ACCESS_HIDDEN)

    class Meta:
        db_table = "form_permissions_rolefieldaccess"
        unique_together = ("role", "form", "group", "field")

    def __str__(self):
        target = self.field.key if self.field else (self.group.name if self.group else "(form)")
        return f"{self.role.name} -> {self.form.code}::{target} = {self.access}"


class AccessTemplate(models.Model):
    """A reusable template grouping RoleFieldAccess-like entries.

    Templates are created by HQ admins and can be applied to roles (or users)
    to generate concrete `RoleFieldAccess` entries.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "form_permissions_accesstemplate"

    def __str__(self):
        return self.name


class TemplateFieldAccess(models.Model):
    template = models.ForeignKey(AccessTemplate, on_delete=models.CASCADE, related_name="fields")
    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE)
    group = models.ForeignKey(FormFieldGroup, on_delete=models.CASCADE, null=True, blank=True)
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, null=True, blank=True)
    access = models.CharField(max_length=20, choices=RoleFieldAccess.ACCESS_CHOICES, default=RoleFieldAccess.ACCESS_HIDDEN)

    class Meta:
        db_table = "form_permissions_templatefieldaccess"
        unique_together = ("template", "form", "group", "field")

    def __str__(self):
        target = self.field.key if self.field else (self.group.name if self.group else "(form)")
        return f"{self.template.code} -> {self.form.code}::{target} = {self.access}"
