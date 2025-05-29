import asyncio
import os
from django.conf import settings
from telegram import Bot, InputMediaPhoto
from urllib.parse import urljoin
from django.conf import settings
from django.urls import reverse
from telegram.error import BadRequest

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
    """Собираем данные синхронно и запускаем async-отправку."""
    chat_id = settings.TELEGRAM_CHAT_ID

    # Синхронно вытаскиваем все OrderItem
    items = list(order.items.select_related('product').all())

    # Собираем media_data
    media_data = []
    for item in items:
        prod = item.product
        if prod.image and prod.image.url:
            media_data.append({
                'url': base_url.rstrip('/') + prod.image.url,
                'caption': f"{prod.name} × {item.quantity} шт."
            })

    # Формируем текст
    lines = [
        f"🆕 Новый заказ #{order.id}",
        f"Пользователь: {order.user.username}",
        "",
        "📦 Состав заказа:"
    ]
    total = 0
    for item in items:
        lines.append(f"- {item.product.name}: {item.quantity} × {item.price} ₽")
        total += item.quantity * item.price
    lines += [
        "",
        f"💰 Всего: {total:.2f} ₽",
        f"📅 Дата доставки: {order.delivery_date} {order.delivery_time}",
        f"🏠 Адрес: {order.delivery_address}",
    ]
    text = "\n".join(lines)

    # Запускаем асинхронную отправку
    asyncio.run(_async_send(chat_id, media_data, text))


async def _async_send(chat_id: int, media_data: list, text: str):
    # Попытка отправить как альбом
    if media_data:
        group = [InputMediaPhoto(media=d['url'], caption=d['caption'])
                 for d in media_data]
        try:
            await bot.send_media_group(chat_id=chat_id, media=group)
        except BadRequest:
            # fallback: шлём по одной картинке
            for d in media_data:
                try:
                    await bot.send_photo(chat_id=chat_id,
                                         photo=d['url'],
                                         caption=d['caption'])
                except BadRequest:
                    # пропускаем, если и это не прокатывает
                    continue

    # Отправляем итоговый текст
    await bot.send_message(chat_id=chat_id, text=text)