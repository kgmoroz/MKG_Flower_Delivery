import asyncio
import os
from django.conf import settings
from telegram import Bot
from urllib.parse import urljoin
from django.conf import settings
from django.urls import reverse

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

def send_order_status_update(order):
    text = (
        f"🔔 Обновлён статус заказа #{order.id}:\n"
        f"{order.get_status_display()}\n"
        f"Пользователь: {order.user.username}\n"
        f"Адрес: {order.delivery_address}\n"
        f"Дата/время: {order.delivery_date} {order.delivery_time}"
    )
    asyncio.run(bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text))


def send_new_order_notification(order, base_url: str):
    """
    Отправляет одно текстовое сообщение с полной информацией о заказе.
    """
    chat_id = settings.TELEGRAM_CHAT_ID

    # Собираем строковый отчёт
    lines = [
        f"🆕 Новый заказ #{order.id}",
        f"Пользователь: {order.user.username}",
        "",
        "📦 Состав заказа:"
    ]
    total = 0
    for item in order.items.select_related('product').all():
        lines.append(f"- {item.product.name}: {item.quantity} × {item.price} ₽")
        total += item.quantity * item.price
    lines += [
        "",
        f"💰 Всего: {total:.2f} ₽",
        f"📅 Дата доставки: {order.delivery_date} {order.delivery_time}",
        f"🏠 Адрес: {order.delivery_address}",
    ]
    text = "\n".join(lines)

    # Асинхронно шлём одно сообщение
    asyncio.run(bot.send_message(chat_id=chat_id, text=text))