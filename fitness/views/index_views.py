from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from ..models import User
from ..decorators import get_session_user


def index(request):
    """Главная страница"""
    return render(request, 'fitness/index.html', {
        'user': get_session_user(request),
    })

def login_view(request):
    """Форма входа"""
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


def logout_view(request):
    """Выход из системы"""
    request.session.flush()
    messages.success(request, 'Вы вышли из системы')
    return redirect('fitness:index')


def api_test(request):
    """Страница для тестирования API с кнопками"""
    return render(request, 'fitness/api_test.html')


def database_schema(request):
    """Страница с визуальной схемой базы данных"""
    return render(request, 'fitness/database_schema.html')
