from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .authentication import get_fitness_user, is_administrator


class IsAdministrator(BasePermission):
    """Доступ только для пользователя с ролью администратора."""

    def has_permission(self, request: Any, view: Any) -> bool:
        """
        Проверка права на выполнение действия.

        Args:
            request: DRF-запрос.
            view: ViewSet или APIView.
        """
        return is_administrator(get_fitness_user(request))


class IsOwnerOrAdministrator(BasePermission):
    """Клиент видит только свои объекты; администратор — все."""

    owner_field = 'user'

    def has_permission(self, request: Any, view: Any) -> bool:
        """
        Проверка базового доступа к списку/созданию.

        Args:
            request: DRF-запрос.
            view: ViewSet или APIView.
        """
        if request.method in SAFE_METHODS:
            return True
        return get_fitness_user(request) is not None

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        """
        Проверка доступа к конкретному объекту.

        Args:
            request: DRF-запрос.
            view: ViewSet или APIView.
            obj: Проверяемый объект.
        """
        user = get_fitness_user(request)
        if is_administrator(user):
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner == user


class ReadOnlyOrAdministrator(BasePermission):
    """Чтение разрешено всем, изменение только администратору."""

    def has_permission(self, request: Any, view: Any) -> bool:
        """
        Проверка доступа к действию.

        Args:
            request: DRF-запрос.
            view: ViewSet или APIView.
        """
        if request.method in SAFE_METHODS:
            return True
        return is_administrator(get_fitness_user(request))
