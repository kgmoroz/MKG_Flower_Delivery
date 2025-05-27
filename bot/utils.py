import asyncio
from django.conf import settings
from telegram import Bot

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