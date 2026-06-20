from typing import Any

from django.db import models
from .user import User
from .fitness_class import FitnessClass


class ClassBooking(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Записан'),
        ('canceled', 'Отменён'),
        ('attended', 'Посетил'),
        ('no_show', 'Не пришёл'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_bookings', verbose_name='Пользователь')
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, verbose_name='Занятие')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked', verbose_name='Статус записи')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время начала')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время окончания')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='updated_class_bookings', verbose_name='Кто изменил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения статуса')

    class Meta:
        verbose_name = 'Запись на занятие'
        verbose_name_plural = 'Записи на занятия'
        ordering = ['-created_at']
        unique_together = [('user', 'fitness_class', 'start_time')]

    def __str__(self) -> str:
        """Строковое представление записи на занятие."""
        class_name = self.fitness_class.name if self.fitness_class else 'Занятие'
        if self.start_time:
            return f'{self.user.full_name} — {class_name} ({self.start_time})'
        return f'{self.user.full_name} — {class_name}'

    def clean(self) -> None:
        """Бизнес-правила для новой клиентской записи."""
        if self.status not in ('booked', 'attended'):
            return
        from ..validators import (
            validate_active_membership,
            validate_class_capacity,
            validate_phone_format,
        )
        validate_class_capacity(self.fitness_class, exclude_booking_id=self.pk)
        validate_active_membership(self.user)
        validate_phone_format(self.user.phone)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение записи на занятие.

        Args:
            *args: Позиционные аргументы Django save().
            **kwargs: Именованные аргументы Django save().
        """
        super().save(*args, **kwargs)
