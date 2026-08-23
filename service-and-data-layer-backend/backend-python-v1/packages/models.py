from django.db import models


class Package(models.Model):
    TYPE_CHOICES = (
        ("internet", "Internet"),
        ("voice", "Voice"),
        ("combo", "Combo"),
        ("enterprise", "Enterprise"),
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("archived", "Archived"),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    speed = models.CharField(max_length=100, blank=True)
    validity_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "packages_package"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
