from django.db import models
from .user import User
from .fitness_class import FitnessClass


class FavoriteClass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_classes', verbose_name='Пользователь')
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, verbose_name='Занятие')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления в избранное')

    class Meta:
        verbose_name = 'Избранное занятие'
        verbose_name_plural = 'Избранные занятия'
        ordering = ['-created_at']
        unique_together = [('user', 'fitness_class')]

    def __str__(self):
        return f'{self.user.full_name} добавил в избранное {self.fitness_class.name}'
