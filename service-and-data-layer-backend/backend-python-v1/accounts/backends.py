from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class AccountsAuthBackend(BaseBackend):
    def authenticate(self, request, phone=None, email=None, password=None, **kwargs):
        if not password:
            return None

        try:
            if phone:
                user = User.objects.get(phone=phone)
            elif email:
                user = User.objects.get(email=email)
            else:
                return None
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
