from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOrUsernameBackend(ModelBackend):
    """Allow login with either username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try email first, then fall back to username
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            if self.user_can_authenticate(user):
                return user
            # Password correct but account is inactive — flag it on the request
            if request is not None:
                request._account_inactive = True
        return None

    def user_can_authenticate(self, user):
        if not super().user_can_authenticate(user):
            return False
        # Superusers bypass the Profil/Compte check
        if user.is_superuser:
            return True
        # Regular users must have an active Profil tied to a non-deleted Compte
        if not hasattr(user, 'profil'):
            return False
        if user.profil.deleted_at is not None:
            return False
        if user.profil.compte_id is None:
            return False
        return True
