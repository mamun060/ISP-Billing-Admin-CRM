from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class Partner(MPTTModel):
    PARTNER_TYPES = (
        ("HQ", "HQ"),
        ("ZONE", "Zone"),
        ("AREA", "Area"),
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=PARTNER_TYPES, default="ZONE")
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        db_table = "partners_partner"

    def __str__(self):
        return self.name


class CommissionAgreementManager(models.Manager):
    def get_active_agreement(self, partner, as_of_date=None):
        as_of_date = as_of_date or timezone.localdate()
        return (
            self.filter(partner=partner)
            .filter(effective_from__lte=as_of_date)
            .filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=as_of_date))
            .order_by("-effective_from")
            .first()
        )


class CommissionAgreement(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="agreements")
    parent = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="child_agreements", null=True, blank=True)
    pool_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    objects = CommissionAgreementManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "partners_commission_agreement"

    def clean(self):
        if self.parent_id is None:
            max_allowed = Decimal("100")
        else:
            active_parent_agreement = CommissionAgreement.objects.get_active_agreement(self.parent, self.effective_from)
            if self.parent.type == "HQ":
                max_allowed = Decimal("100")
            elif active_parent_agreement is None:
                max_allowed = None
            else:
                max_allowed = active_parent_agreement.pool_percentage

        if max_allowed is not None and self.pool_percentage > max_allowed:
            raise ValidationError(
                {"pool_percentage": f"Pool percentage exceeds the parent cap of {max_allowed}%."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.partner.name} ({self.pool_percentage}%)"


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


class Division(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partners_division"

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=255)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="districts")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partners_district"

    def __str__(self):
        return self.name


class Upazila(models.Model):
    name = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="upazilas")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partners_upazila"

    def __str__(self):
        return self.name


class Union(models.Model):
    name = models.CharField(max_length=255)
    upazila = models.ForeignKey(Upazila, on_delete=models.CASCADE, related_name="unions")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partners_union"

    def __str__(self):
        return self.name
