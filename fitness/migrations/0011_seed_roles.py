from django.db import migrations


def seed_roles(apps, schema_editor):
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
