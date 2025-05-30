import pytest
from django.contrib.auth import get_user_model
from catalog.models import Product
from orders.models import Order, OrderItem

User = get_user_model()

@pytest.fixture
def user(db):
    """Тестовый пользователь с заполненным именем/фамилией."""
    return User.objects.create_user(
        username='testuser',
        password='pass1234',
        first_name='Иван',
        last_name='Петров',
        email='ivan@example.com'
    )

@pytest.fixture
def user_no_name(db):
    """Тестовый пользователь без имени/фамилии (только username)."""
    return User.objects.create_user(
        username='nousername',
        password='pass1234',
        first_name='',
        last_name='',
        email='nouser@example.com'
    )

@pytest.fixture
def product1(db):
    return Product.objects.create(name="Роза", price=500)

@pytest.fixture
def product2(db):
    return Product.objects.create(name="Лилия", price=700)

@pytest.fixture
def order(db, user, product1, product2):
    """Заказ с двумя позициями: 2×Роза, 1×Лилия."""
    order = Order.objects.create(
        user=user,
        status='PENDING',
        delivery_date="2025-06-01",
        delivery_time="12:00",
        delivery_address="ул. Тестовая, д.1",
    )
    OrderItem.objects.create(order=order, product=product1, quantity=2, price=500)
    OrderItem.objects.create(order=order, product=product2, quantity=1, price=700)
    return order
