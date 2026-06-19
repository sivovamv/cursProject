# Курсовая работа: Фитнес-центр

## Описание проекта

Веб-сайт для фитнес-центра с административной панелью Django.

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Выполните миграции базы данных:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Создайте суперпользователя для доступа к админке:
```bash
python manage.py createsuperuser
```

4. Запустите сервер разработки:
```bash
python manage.py runserver
```

5. Откройте админ-панель в браузере:
```
http://127.0.0.1:8000/admin/
```

## Структура базы данных

Проект содержит следующие модели:
- Role (Роли пользователей)
- User (Пользователи)
- Trainer (Тренеры)
- FitnessClass (Занятия)
- TariffType (Типы абонементов)
- Membership (Абонементы)
- ClassBooking (Записи на занятия)
- FavoriteClass (Избранные занятия)
