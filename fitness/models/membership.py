from django.db import models
from .user import User
from .tariff_type import TariffType


class Membership(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('frozen', 'Заморожен'),
        ('expired', 'Завершён'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships', verbose_name='Пользователь')
    tariff_type = models.ForeignKey(TariffType, on_delete=models.PROTECT, verbose_name='Тип абонемента')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='created_memberships', verbose_name='Кто создал')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='updated_memberships', verbose_name='Кто изменил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменено')

    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
        ordering = ['-start_date']

    def __str__(self) -> str:
        """Строковое представление абонемента."""
        return f'{self.user.full_name} - {self.tariff_type.name} ({self.start_date} - {self.end_date})'
