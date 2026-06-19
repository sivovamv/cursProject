from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitness', '0007_merge_workout_type_into_fitness_class'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalfitnessclass',
            name='title',
        ),
        migrations.RemoveField(
            model_name='historicalfitnessclass',
            name='start_time',
        ),
        migrations.RemoveField(
            model_name='historicalfitnessclass',
            name='end_time',
        ),
        migrations.AlterField(
            model_name='historicalfitnessclass',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
    ]
