from django.db import models
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField("название", max_length=200)
    description = models.TextField("описание", blank=True)
    price = models.DecimalField("цена", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField("изображение", upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name