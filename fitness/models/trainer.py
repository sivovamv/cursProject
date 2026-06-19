from django.db import models
from .user import User


class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    specialization = models.CharField(max_length=150, verbose_name='Специализация')
    bio = models.TextField(blank=True, verbose_name='Биография')
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True, verbose_name='Фотография')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_trainers', verbose_name='Кто создал')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='updated_trainers', verbose_name='Кто изменил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменено')

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'
        ordering = ['user__full_name']

    def __str__(self):
        return f'{self.user.full_name} - {self.specialization}'
