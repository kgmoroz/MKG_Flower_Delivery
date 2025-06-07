import pytest
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from catalog.cart_utils import get_cart, save_cart, total_items

def _get_request_with_session():
    """
    Вспомогательная функция: создаёт request и приклёпывает к нему session.
    """
    rf = RequestFactory()
    request = rf.get('/')
    # Привязка SessionMiddleware, чтобы появился request.session
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request

@pytest.mark.django_db
def test_get_cart_returns_empty_by_default():
    request = _get_request_with_session()
    # Пустая сессия → пустая корзина
    assert get_cart(request) == {}

@pytest.mark.django_db
def test_save_cart_sets_session_and_marks_modified():
    request = _get_request_with_session()
    cart = {'1': 2, '5': 3}
    # Сохраняем корзину
    save_cart(request, cart)
    # Session должен содержать ключ 'cart'
    assert request.session.get('cart') == cart
    # И session.modified должно быть True
    assert request.session.modified is True

def test_total_items_sums_values():
    # total_items просто суммирует все значения словаря
    assert total_items({}) == 0
    assert total_items({'1': 2, '3': 5, '7': 1}) == 8
