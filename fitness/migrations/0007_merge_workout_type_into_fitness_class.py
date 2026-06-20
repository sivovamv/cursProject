from typing import Any

from django.db import migrations, models


def copy_workout_type_to_fitness_class(apps: Any, schema_editor: Any) -> None:
    """
    Перенос названия и описания типа тренировки в занятие.

    Args:
        apps: Реестр моделей миграции.
        schema_editor: Редактор схемы БД.
    """
    FitnessClass = apps.get_model('fitness', 'FitnessClass')
    for fitness_class in FitnessClass.objects.select_related('workout_type').all():
        workout_type = fitness_class.workout_type
        if workout_type:
            fitness_class.name = workout_type.name
            fitness_class.description = workout_type.description or ''
        else:
            fitness_class.name = f'Занятие #{fitness_class.pk}'
            fitness_class.description = ''
        fitness_class.save(update_fields=['name', 'description'])


def copy_workout_type_to_historical_fitness_class(apps: Any, schema_editor: Any) -> None:
    """
    Перенос названия и описания типа тренировки в исторические записи занятий.

    Args:
        apps: Реестр моделей миграции.
        schema_editor: Редактор схемы БД.
    """
    HistoricalFitnessClass = apps.get_model('fitness', 'HistoricalFitnessClass')
    WorkoutType = apps.get_model('fitness', 'WorkoutType')
    workout_types = {wt.pk: wt for wt in WorkoutType.objects.all()}

    for record in HistoricalFitnessClass.objects.all():
        workout_type = workout_types.get(record.workout_type_id)
        if workout_type:
            record.name = workout_type.name
            record.description = workout_type.description or ''
        elif record.workout_type_id:
            record.name = f'Занятие #{record.id}'
            record.description = ''
        else:
            record.name = record.name or f'Занятие #{record.id}'
            record.description = record.description or ''
        record.save(update_fields=['name', 'description'])


class Migration(migrations.Migration):

    dependencies = [
        ('fitness', '0006_remove_historicalfitnessclass_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitnessclass',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='Название занятия'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fitnessclass',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='historicalfitnessclass',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='Название занятия'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalfitnessclass',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.RunPython(copy_workout_type_to_fitness_class, migrations.RunPython.noop),
        migrations.RunPython(copy_workout_type_to_historical_fitness_class, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='fitnessclass',
            name='workout_type',
        ),
        migrations.RemoveField(
            model_name='historicalfitnessclass',
            name='workout_type',
        ),
        migrations.DeleteModel(
            name='WorkoutType',
        ),
    ]
