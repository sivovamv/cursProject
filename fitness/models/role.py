from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название роли')
    description = models.TextField(blank=True, verbose_name='Описание роли')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self) -> str:
        """Строковое представление роли."""
        return self.name
