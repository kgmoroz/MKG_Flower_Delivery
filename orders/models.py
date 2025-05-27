from django.db import models
from django.conf import settings
from catalog.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Принят к работе"),
        ("PROCESSING", "В работе"),
        ("DELIVERING", "В доставке"),
        ("COMPLETED", "Выполнен"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="пользователь")
    status = models.CharField("статус", max_length=20, choices=STATUS_CHOICES, default="PENDING")
    delivery_date = models.DateField("дата доставки")
    delivery_time = models.TimeField("время доставки")
    delivery_address = models.CharField("адрес доставки", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Заказ #{self.id} — {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("количество", default=1)
    price = models.DecimalField("цена на момент заказа", max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}×{self.product.name} (заказ #{self.order.id})"