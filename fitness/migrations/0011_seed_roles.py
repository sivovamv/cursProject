from typing import Any

from django.db import migrations


def seed_roles(apps: Any, schema_editor: Any) -> None:
    """
    Создание базовых ролей пользователей.

    Args:
        apps: Реестр моделей миграции.
        schema_editor: Редактор схемы БД.
    """
    Role = apps.get_model('fitness', 'Role')
    roles = [
        ('Администратор', 'Полный доступ к управлению фитнес-центром'),
        ('Клиент', 'Запись на занятия, абонементы, отзывы'),
    ]
    for name, description in roles:
        Role.objects.get_or_create(name=name, defaults={'description': description})


class Migration(migrations.Migration):

    dependencies = [
        ('fitness', '0010_user_is_blocked_classreview'),
    ]

    operations = [
        migrations.RunPython(seed_roles, migrations.RunPython.noop),
    ]
