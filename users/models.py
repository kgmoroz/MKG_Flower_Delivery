from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField("телефон", max_length=20, blank=True)
    address = models.CharField("адрес доставки", max_length=255, blank=True)

    def __str__(self):
        return self.username