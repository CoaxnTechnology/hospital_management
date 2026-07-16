import logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class EmailOrUsernameBackend(ModelBackend):
    """Allow login with either username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info("LOGIN_ATTEMPT username=%s", username)

        try:
            user = User.objects.get(email=username)
            logger.info("LOGIN_FOUND_BY_EMAIL username=%s email=%s active=%s",
                        user.username, username, user.is_active)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
                logger.info("LOGIN_FOUND_BY_USERNAME username=%s active=%s",
                            username, user.is_active)
            except User.DoesNotExist:
                logger.warning("LOGIN_USER_NOT_FOUND username=%s", username)
                return None

        password_ok = user.check_password(password)
        logger.info("LOGIN_PASSWORD_CHECK username=%s result=%s",
                    user.username, password_ok)

        if password_ok:
            can_auth = self.user_can_authenticate(user)
            logger.info("LOGIN_CAN_AUTHENTICATE username=%s result=%s",
                        user.username, can_auth)
            if can_auth:
                return user
            if request is not None:
                request._account_inactive = True
                logger.warning("LOGIN_ACCOUNT_INACTIVE username=%s is_active=%s has_profil=%s",
                               user.username, user.is_active, hasattr(user, 'profil'))
        return None

    def user_can_authenticate(self, user):
        if not super().user_can_authenticate(user):
            logger.info("AUTH_FAILED_DEFAULT is_active=%s", user.is_active)
            return False
        if user.is_superuser:
            return True
        if not hasattr(user, 'profil'):
            logger.warning("AUTH_FAILED_NO_PROFIL username=%s", user.username)
            return False
        if user.profil.deleted_at is not None:
            logger.warning("AUTH_FAILED_PROFIL_DELETED username=%s deleted_at=%s",
                           user.username, user.profil.deleted_at)
            return False
        if user.profil.compte_id is None:
            logger.warning("AUTH_FAILED_NO_COMPTE username=%s", user.username)
            return False
        return True
