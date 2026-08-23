from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q

User = get_user_model()


class AccountsAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, phone=None, email=None, password=None, **kwargs):
        if not password:
            return None

        identifier = username or phone or email
        if not identifier:
            return None

        user = (
            User.objects.filter(
                Q(username__iexact=identifier)
                | Q(phone__iexact=identifier)
                | Q(email__iexact=identifier)
            )
            .order_by("id")
            .first()
        )

        if user is None:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        """Return True if the user is allowed to authenticate.

        Mirrors Django's ModelBackend.user_can_authenticate behaviour: deny
        authentication for users with is_active=False, allow if attribute is
        missing.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
