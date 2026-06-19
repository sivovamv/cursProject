from django.db import models
from .role import Role


class User(models.Model):
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    password_hash = models.CharField(max_length=255, verbose_name='Хэш пароля')
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name='Роль')
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def is_administrator(self):
        from ..constants import ROLE_ADMIN
        return self.role.name == ROLE_ADMIN

    @property
    def is_client(self):
        from ..constants import ROLE_CLIENT
        return self.role.name == ROLE_CLIENT
