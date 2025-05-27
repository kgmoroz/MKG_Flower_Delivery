import asyncio
from django.conf import settings
from telegram import Bot
from urllib.parse import urljoin

def send_order_status_update(order):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
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
    Отправляет сообщение о новом заказе в Telegram.
    Если у первого товара есть изображение, шлёт его как фото с подписью.
    """
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    # Готовим текст
    text = (
        f"🆕 Новый заказ #{order.id}\n"
        f"Пользователь: {order.user.username}\n"
        f"Сумма: {sum(item.quantity * item.price for item in order.items.all())} ₽\n"
        f"Дата доставки: {order.delivery_date} {order.delivery_time}\n"
        f"Адрес: {order.delivery_address}"
    )

    # Попытаемся найти фото первого букета
    first_item = order.items.first()
    if first_item and first_item.product.image:
        # Формируем абсолютный URL к изображению
        image_url = urljoin(base_url, first_item.product.image.url)
        # Отправляем фото с подписью
        asyncio.run(bot.send_photo(
            chat_id=settings.TELEGRAM_CHAT_ID,
            photo=image_url,
            caption=text
        ))
    else:
        # Если нет фото — обычное текстовое сообщение
        asyncio.run(bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text
        ))