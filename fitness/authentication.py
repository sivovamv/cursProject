from typing import Any

from django.http import HttpRequest
from rest_framework.authentication import SessionAuthentication

from .constants import ROLE_ADMIN
from .models import User


class FitnessSessionAuthentication(SessionAuthentication):
    """Сессионная аутентификация для API на основе fitness.User."""

    def authenticate(self, request: HttpRequest) -> tuple[User, None] | None:
        """
        Аутентификация API по user_id в сессии.

        Args:
            request: HTTP-запрос DRF/Django.
        """
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


def get_fitness_user(request: HttpRequest) -> User | None:
    """
    Получение доменного пользователя fitness.User из request.user.

    Args:
        request: HTTP-запрос.
    """
    user = getattr(request, 'user', None)
    if isinstance(user, User):
        return user
    return None


def is_administrator(user: Any) -> bool:
    """
    Проверка роли администратора.

    Args:
        user: Объект пользователя или AnonymousUser.
    """
    return (
        isinstance(user, User)
        and user.role_id
        and user.role.name == ROLE_ADMIN
    )
