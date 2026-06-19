from rest_framework.permissions import BasePermission, SAFE_METHODS

from .authentication import get_fitness_user, is_administrator


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return is_administrator(get_fitness_user(request))


class IsOwnerOrAdministrator(BasePermission):
    """Клиент видит только свои объекты; администратор — все."""

    owner_field = 'user'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return get_fitness_user(request) is not None

    def has_object_permission(self, request, view, obj):
        user = get_fitness_user(request)
        if is_administrator(user):
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner == user


class ReadOnlyOrAdministrator(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return is_administrator(get_fitness_user(request))
