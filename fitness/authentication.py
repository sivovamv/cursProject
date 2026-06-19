from rest_framework.authentication import BaseAuthentication, SessionAuthentication

from .constants import ROLE_ADMIN
from .models import User


class FitnessSessionAuthentication(SessionAuthentication):
    """Сессионная аутентификация для API на основе fitness.User."""

    def authenticate(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return None
        try:
            user = User.objects.select_related('role').get(pk=user_id)
        except User.DoesNotExist:
            return None
        if getattr(user, 'is_blocked', False):
            return None
        return (user, None)


def get_fitness_user(request):
    user = getattr(request, 'user', None)
    if isinstance(user, User):
        return user
    return None


def is_administrator(user):
    return (
        isinstance(user, User)
        and user.role_id
        and user.role.name == ROLE_ADMIN
    )
