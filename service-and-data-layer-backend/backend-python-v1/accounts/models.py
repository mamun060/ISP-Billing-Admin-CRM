from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from partners.models import Partner


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone=None, email=None, username=None, password=None, **extra_fields):
        if not phone and not email and not username:
            raise ValueError("Users must have either a username, phone number, or email address.")

        email = self.normalize_email(email) if email else None
        username = username or (phone or email.split("@", 1)[0] if email else None)
        user = self.model(phone=phone, email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone=None, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone=phone, email=email, username=username, password=password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_display_name()

    @property
    def login_identifier(self):
        return self.username or self.phone or self.email

    def get_display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.phone or self.email or "User"

    def save(self, *args, **kwargs):
        if not self.username:
            if self.phone:
                self.username = self.phone
            elif self.email:
                self.username = self.email.split("@", 1)[0]
        super().save(*args, **kwargs)

    def has_permission_code(self, permission_code):
        return self.user_roles.filter(role__permissions__code=permission_code).exists()

    @property
    def roles(self):
        return self.user_roles.select_related("role").prefetch_related("role__permissions").all()


class Role(models.Model):
    SCOPE_TYPES = (
        ("system", "System"),
        ("partner", "Partner"),
        ("zone", "Zone"),
        ("area", "Area"),
    )

    name = models.CharField(max_length=100, unique=True)
    scope_type = models.CharField(max_length=20, choices=SCOPE_TYPES, default="partner")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_role"

    def __str__(self):
        return self.name


class Permission(models.Model):
    code = models.CharField(max_length=150, unique=True)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_permission"

    def __str__(self):
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="roles")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_role_permission"
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_user_role"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} -> {self.role.name}"
