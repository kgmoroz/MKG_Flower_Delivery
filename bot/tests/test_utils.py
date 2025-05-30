import pytest
from django.conf import settings
from bot import utils

@pytest.mark.django_db
def test_send_new_order_notification(monkeypatch, order, user):
    calls = []
    async def fake_send_message(self, chat_id, text, *args, **kwargs):
        calls.append((chat_id, text))

    # Патчим метод класса Bot для перехвата send_message
    monkeypatch.setattr(type(utils.bot), 'send_message', fake_send_message)
    # Устанавливаем тестовый chat_id
    monkeypatch.setattr(settings, 'TELEGRAM_CHAT_ID', 123)

    # Вызываем функцию
    utils.send_new_order_notification(order, base_url='http://testserver')

    assert len(calls) == 1, "Ожидалось одно сообщение"
    chat_id, text = calls[0]
    assert chat_id == 123
    assert f"🆕 Новый заказ #{order.id}" in text
    assert f"({order.user.username})" in text
    assert "📦 Состав заказа:" in text
    total = sum(i.quantity * i.price for i in order.items.all())
    assert f"💰 Всего: {total:.2f} ₽" in text

@pytest.mark.django_db
def test_send_order_status_update(monkeypatch, order, user):
    calls = []
    async def fake_send_message(self, chat_id, text, *args, **kwargs):
        calls.append((chat_id, text))

    # Патчим метод класса Bot для send_message
    monkeypatch.setattr(type(utils.bot), 'send_message', fake_send_message)
    monkeypatch.setattr(settings, 'TELEGRAM_CHAT_ID', 456)

    # Меняем статус заказа
    order.status = 'COMPLETED'
    order.save()
    utils.send_order_status_update(order)

    assert len(calls) == 1, "Ожидался один вызов"
    chat_id, text = calls[0]
    assert chat_id == 456
    assert f"🔔 Обновлён статус заказа #{order.id}" in text
    full_name = order.user.get_full_name().strip() or order.user.username
    assert f"{full_name} ({order.user.username})" in text
