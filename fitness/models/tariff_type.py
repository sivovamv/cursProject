from django.db import models


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

    def __str__(self):
        return self.name

    def clean(self):
        from ..validators import validate_membership_price
        validate_membership_price(self.price)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
