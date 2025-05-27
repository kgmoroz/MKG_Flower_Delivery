from django.contrib import admin
from .models import Order, OrderItem
from bot.utils import send_order_status_update

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "delivery_date", "delivery_time")
    list_filter = ("status",)
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        # Сохраняем старый статус
        old_status = None
        if change:
            old = Order.objects.get(pk=obj.pk)
            old_status = old.status
        super().save_model(request, obj, form, change)
        # Если статус изменился — шлём уведомление
        if change and old_status != obj.status:
            send_order_status_update(obj)