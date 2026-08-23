from __future__ import annotations

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Partner(MPTTModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        db_table = "partners_partner"

    def __str__(self):
        return self.name


class Zone(models.Model):
    name = models.CharField(max_length=255)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="zones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "partners_zone"

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=255)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="areas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "partners_area"

    def __str__(self):
        return self.name
