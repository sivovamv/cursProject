from django.db import models
from typing import Any


class TariffType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название тарифа')
    duration_days = models.PositiveIntegerField(verbose_name='Длительность (дней)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Тип абонемента'
        verbose_name_plural = 'Типы абонементов'
        ordering = ['name']

    def __str__(self) -> str:
        """Строковое представление типа абонемента."""
        return self.name

    def clean(self) -> None:
        """Проверка бизнес-правил тарифа перед сохранением."""
        from ..validators import validate_membership_price
        validate_membership_price(self.price)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение тарифа с предварительной валидацией.

        Args:
            *args: Позиционные аргументы Django save().
            **kwargs: Именованные аргументы Django save().
        """
        self.full_clean()
        super().save(*args, **kwargs)
