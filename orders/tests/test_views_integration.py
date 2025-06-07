import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from datetime import timedelta, time

from catalog.models import Product
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def create_user(db):
    """
    Фикстура для создания обычного пользователя.
    Возвращает функцию make_user(username, password).
    """
    def make_user(username='testuser', password='password123'):
        return User.objects.create_user(username=username, password=password)
    return make_user

@pytest.fixture
def create_product(db):
    """
    Фикстура для быстрого создания товара.
    Возвращает функцию make_product(name, price, **kwargs).
    """
    def make_product(name='Тестовый букет', price=500, **kwargs):
        return Product.objects.create(name=name, price=price, **kwargs)
    return make_product

@pytest.mark.django_db
def test_full_order_flow(client, create_user, create_product):
    """
    Интеграционный тест «от корзины до оформления заказа».

    Шаги:
    1) Создать пользователя и залогиниться.
    2) Создать один товар через ORM.
    3) Добавить товар в корзину (POST на catalog:add_to_cart).
    4) Зайти на страницу оформления заказа (orders:checkout) и получить форму.
    5) Отправить POST с валидными данными (дата+время в будущем, адрес).
    6) Убедиться, что происходит редирект на страницу благодарности (orders:thank_you).
    7) Проверить, что в базе появился объект Order, и что у него есть правильные OrderItem.
    """

    # 1) Создаём пользователя и логинимся
    user = create_user(username='alice', password='secret123')
    login_successful = client.login(username='alice', password='secret123')
    assert login_successful, "Не удалось залогиниться тестовым пользователем"

    # 2) Создаём один товар
    p = create_product(name='Лаванда', price=750)

    # 3) Добавляем товар в корзину
    url_add = reverse('catalog:add_to_cart', args=[p.id])
    response_add = client.post(url_add, data={'quantity': 3})
    assert response_add.status_code == 302
    # После добавления корзину видно на catalog:cart
    assert response_add.url == reverse('catalog:cart')

    # 4) GET на страницу /orders/checkout/ чтобы получить форму
    url_checkout = reverse('orders:checkout')
    response_get = client.get(url_checkout)
    assert response_get.status_code == 200

    # 5) Подготавливаем данные для POST: дата/время + адрес
    tomorrow = timezone.localdate() + timedelta(days=1)
    # Время — в середине рабочего дня (например, 10:00)
    delivery_time = time(hour=10, minute=0)
    form_data = {
        'delivery_date':    tomorrow.strftime('%Y-%m-%d'),
        'delivery_time':    delivery_time.strftime('%H:%M'),
        'delivery_address': 'ул. Тестовая, д.42',
    }

    # Отправляем POST на оформление
    response_post = client.post(url_checkout, data=form_data)
    # Если всё валидно, должен быть редирект на thank_you
    assert response_post.status_code == 302
    # Получаем ID заказа из URL редиректа
    expected_order = Order.objects.filter(user=user).first()
    assert expected_order is not None, "Заказ не создался"
    url_thank = reverse('orders:thank_you', args=[expected_order.id])
    assert response_post.url == url_thank

    # 6) Убедимся, что OrderItem создан правильно
    items = OrderItem.objects.filter(order=expected_order)
    assert items.count() == 1, "В заказе должен быть ровно один OrderItem"
    item = items.first()
    assert item.product == p
    assert item.quantity == 3
    assert float(item.price) == float(p.price)

    # 7) Проверим, что общая сумма через метод total_amount() совпадает: 3×750 = 2250
    total = expected_order.total_amount()
    assert float(total) == 3 * float(p.price)
