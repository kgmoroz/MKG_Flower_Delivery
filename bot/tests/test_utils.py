import pytest
import datetime
from telegram import InputMediaPhoto
from bot import utils

@pytest.mark.django_db
def test_send_new_order_notification_text_only(monkeypatch, order, user):
    """
    Проверяем, что при отсутствии изображений или в упрощённом режиме
    бот получает корректный текст и chat_id.
    """
    sent = []

    # Заглушаем метод send_message и send_media_group
    async def fake_send_message(chat_id, text):
        sent.append(('message', chat_id, text))

    async def fake_send_media_group(chat_id, media):
        sent.append(('media_group', chat_id, media))

    monkeypatch.setattr(utils, 'bot', utils.bot)           # оставляем бот-экземпляр
    monkeypatch.setattr(utils.bot, 'send_message', fake_send_message)
    monkeypatch.setattr(utils.bot, 'send_media_group', fake_send_media_group)

    # Удаляем у всех продуктов изображение, чтобы media_group ветка тоже отработала пустой
    for item in order.items.all():
        item.product.image = None

    # Вызываем
    utils.send_new_order_notification(order, base_url='http://testserver')

    # Должен быть ровно один вызов send_message с правильным текстом
    msgs = [args for kind, *_ , args in sent if kind == 'message']
    assert msgs, "Bot.send_message не был вызван"
    text = msgs[0]
    assert f"Новый заказ #{order.id}" in text
    assert user.username in text
    assert "Состав заказа:" in text
    # Сумма: 2×500 + 1×700 = 1700
    assert "1700.00" in text or "1700" in text

@pytest.mark.django_db
def test_send_order_status_update(monkeypatch, order, user):
    """
    Проверяем, что send_order_status_update шлёт сообщение о новом статусе
    и форматирует пользователя как Имя Фамилия (username).
    """
    sent = []

    async def fake_send_message(chat_id, text):
        sent.append((chat_id, text))

    monkeypatch.setattr(utils, 'bot', utils.bot)
    monkeypatch.setattr(utils.bot, 'send_message', fake_send_message)

    # Дадим заказу статус COMPLETED и вызовем
    order.status = 'COMPLETED'
    utils.send_order_status_update(order)

    assert sent, "Bot.send_message не был вызван"
    chat_id, text = sent[0]
    # Проверяем содержание
    assert f"🔔 Обновлён статус заказа #{order.id}" in text
    full_name = order.user.get_full_name() or order.user.username
    assert f"{full_name} ({order.user.username})" in text
