from django.core.management.base import BaseCommand
from fitness.models import Membership, FitnessClass
from datetime import date, timedelta
from typing import Any


class Command(BaseCommand):
    help = 'Экспорт данных: активные абонементы и занятия за последний месяц'

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Экспорт краткой статистики по активным абонементам и занятиям.

        Args:
            *args: Позиционные аргументы management-команды.
            **options: Опции management-команды.
        """
        # Экспорт активных абонементов
        active_memberships = Membership.objects.filter(
            status='active',
            end_date__gte=date.today()
        )
        
        self.stdout.write(f'Активных абонементов: {active_memberships.count()}')
        for membership in active_memberships[:10]:
            self.stdout.write(
                f'  - {membership.user.full_name}: {membership.start_date} - {membership.end_date}'
            )
        
        # Экспорт занятий за последний месяц
        month_ago = date.today() - timedelta(days=30)
        recent_classes = FitnessClass.objects.filter(created_at__gte=month_ago)
        
        self.stdout.write(f'\nЗанятий за последний месяц: {recent_classes.count()}')
        for fitness_class in recent_classes[:10]:
            workout_name = fitness_class.name
            trainer_name = fitness_class.trainer.user.full_name if fitness_class.trainer else 'N/A'
            self.stdout.write(f'  - {workout_name} (тренер: {trainer_name})')
        
        self.stdout.write(self.style.SUCCESS('Экспорт завершен'))
