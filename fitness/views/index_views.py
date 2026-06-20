from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from ..models import User
from ..decorators import get_session_user


def index(request: HttpRequest) -> HttpResponse:
    """
    Главная страница проекта.

    Args:
        request: HTTP-запрос.
    """
    return render(request, 'fitness/index.html', {
        'user': get_session_user(request),
    })

def login_view(request: HttpRequest) -> HttpResponse:
    """
    Вход пользователя фитнес-центра.

    Args:
        request: HTTP-запрос с email и паролем.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Заполните все поля')
            return render(request, 'fitness/login.html')
        
        try:
            user = User.objects.select_related('role').get(email=email)
            if user.is_blocked:
                messages.error(request, 'Аккаунт заблокирован. Обратитесь к администратору.')
                return render(request, 'fitness/login.html')
            # Проверяем пароль
            # Если пароль хеширован через Django (начинается с pbkdf2_)
            if user.password_hash.startswith('pbkdf2_'):
                if check_password(password, user.password_hash):
                    request.session['user_id'] = user.id
                    request.session['user_email'] = user.email
                    request.session['user_name'] = user.full_name
                    messages.success(request, f'Вы успешно вошли в систему, {user.full_name}')
                    return redirect('fitness:index')
                else:
                    messages.error(request, 'Неверный пароль')
            else:
                # Если пароль не хеширован, проверяем напрямую
                # ВНИМАНИЕ: Это небезопасно, но для совместимости со старыми данными
                if password == user.password_hash:
                    # Обновляем на хешированный пароль
                    user.password_hash = make_password(password)
                    user.save()
                    request.session['user_id'] = user.id
                    request.session['user_email'] = user.email
                    request.session['user_name'] = user.full_name
                    messages.success(request, f'Вы успешно вошли в систему, {user.full_name}')
                    return redirect('fitness:index')
                else:
                    messages.error(request, 'Неверный пароль')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')
        except Exception as e:
            messages.error(request, f'Ошибка входа: {str(e)}')
    
    return render(request, 'fitness/login.html')


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Выход пользователя из системы.

    Args:
        request: HTTP-запрос.
    """
    request.session.flush()
    messages.success(request, 'Вы вышли из системы')
    return redirect('fitness:index')


def api_test(request: HttpRequest) -> HttpResponse:
    """
    Страница для ручного тестирования API.

    Args:
        request: HTTP-запрос.
    """
    return render(request, 'fitness/api_test.html')


def database_schema(request: HttpRequest) -> HttpResponse:
    """
    Страница визуальной схемы базы данных.

    Args:
        request: HTTP-запрос.
    """
    return render(request, 'fitness/database_schema.html')


def sentry_debug(request: HttpRequest) -> HttpResponse:
    """
    Тестовая ошибка для проверки интеграции Sentry.

    Args:
        request: HTTP-запрос.
    """
    if not settings.DEBUG:
        raise Http404
    raise RuntimeError('Sentry test error from fitness center project')
