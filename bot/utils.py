import asyncio
import os
from django.conf import settings
from telegram import Bot
from urllib.parse import urljoin
from django.conf import settings
from django.urls import reverse

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def send_order_status_update(order):
    """
    Уведомляет в Telegram об изменении статуса заказа.
    Формат пользователя: Имя Фамилия (username)
    """
    # собираем имя пользователя
    full_name = order.user.get_full_name().strip() or order.user.username
    user_line = f"{full_name} ({order.user.username})"

    # формируем текст
    text = (
        f"🔔 Обновлён статус заказа #{order.id}:\n"
        f"{order.get_status_display()}\n"
        f"{user_line}\n"
        f"Адрес: {order.delivery_address}\n"
        f"Дата/время: {order.delivery_date} {order.delivery_time}"
    )

    # отправляем в своём loop, защищаясь от ошибок
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)
        )
    except Exception as e:
        print(f"Telegram status update failed: {e!r}")
    finally:
        loop.close()


def send_new_order_notification(order, base_url: str):
    """
    Синхронно собирает текст и отправляет его в Telegram.
    Каждое сообщение уходит в своём собственном event loop, чтобы
    не ломаться из-за «Event loop is closed».
    """
    chat_id = settings.TELEGRAM_CHAT_ID

    # — 1) Формируем текст уведомления —
    lines = [
        f"🆕 Новый заказ #{order.id}",
        # формат «Имя Фамилия (username)»
        *(lambda user: (
            [f"{(user.get_full_name().strip() or user.username)} ({user.username})"]
        ))(order.user),
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
        "",
        f"📅 Дата доставки: {order.delivery_date} {order.delivery_time}",
        f"🏠 Адрес: {order.delivery_address}",
    ]
    text = "\n".join(lines)

    # — 2) Отправляем в Telegram в своём event loop —
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.send_message(chat_id=chat_id, text=text))
    except Exception as e:
        # чтобы checkout не падал, просто выводим в консоль
        print(f"Telegram notification failed: {e!r}")
    finally:
        loop.close()