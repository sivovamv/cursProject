from functools import wraps
from typing import Any, Callable

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import User


def login_required(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """
    Декоратор проверки входа пользователя фитнес-центра.

    Args:
        view_func: Представление, которое требует авторизации.
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Проверяет сессию и передаёт пользователя в request.fitness_user.

        Args:
            request: HTTP-запрос.
        """
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Войдите в систему.')
            return redirect('fitness:login')
        try:
            user = User.objects.select_related('role').get(pk=user_id)
        except User.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Сессия недействительна. Войдите снова.')
            return redirect('fitness:login')
        if user.is_blocked:
            request.session.flush()
            messages.error(request, 'Аккаунт заблокирован.')
            return redirect('fitness:login')
        request.fitness_user = user
        return view_func(request, *args, **kwargs)

    return wrapper


def get_session_user(request: HttpRequest) -> User | None:
    """
    Получение текущего пользователя из сессии.

    Args:
        request: HTTP-запрос.
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.select_related('role').get(pk=user_id)
    except User.DoesNotExist:
        return None
