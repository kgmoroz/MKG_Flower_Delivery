from django.contrib import admin
from .models import Order, OrderItem
from bot.utils import send_order_status_update


# ---------- позиции заказа прямо в форме ------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price')
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0
    can_delete = False


# ---------- сам заказ --------------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Что показываем в списке
    list_display = (
        "id", "user", "created_at",
        "delivery_date", "status", "total_amount",
    )
    list_filter = ("status", "delivery_date")
    search_fields = ("id", "user__username", "user__email")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)          # запретим править вручную

    inlines = [OrderItemInline]

    # ---- быстрые действия статуса ----
    actions = ["mark_processing", "mark_delivering", "mark_completed"]

    @admin.action(description="↪️ Пометить «В работе»")
    def mark_processing(self, request, queryset):
        self._bulk_update_status(queryset, "PROCESSING")

    @admin.action(description="🚚 Пометить «В доставке»")
    def mark_delivering(self, request, queryset):
        self._bulk_update_status(queryset, "DELIVERING")

    @admin.action(description="✅ Пометить «Выполнен»")
    def mark_completed(self, request, queryset):
        self._bulk_update_status(queryset, "COMPLETED")

    # --- колонка «Сумма» ---
    @admin.display(description="Сумма")
    def total_amount(self, obj):
        return sum(i.quantity * i.price for i in obj.items.all())

    # --- служебный метод для bulk-actions ---
    def _bulk_update_status(self, queryset, new_status):
        for order in queryset:
            if order.status != new_status:
                order.status = new_status
                order.save()                   # триггерит save_model()
                send_order_status_update(order)

    # --- единичное сохранение через форму ---
    def save_model(self, request, obj, form, change):
        # запоминаем старый статус, если запись уже существовала
        old_status = None
        if change:
            old_status = Order.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        # если статус изменился вручную — отправляем уведомление
        if change and old_status != obj.status:
            send_order_status_update(obj)
