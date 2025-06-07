from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email   = models.EmailField('e-mail', unique=True)
    phone   = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес доставки', blank=True)

    REQUIRED_FIELDS = ['email']          # обязательно кроме username / password

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
