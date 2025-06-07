import pytest
from django.urls import reverse
from django.test import Client
from django.db import transaction

from catalog.models import Product

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def create_product(db):
    """
    Фикстура позволяет быстро создать один товар.
    Возвращает функцию make_product(name, price, **kwargs).
    """
    def make_product(name='Тестовый букет', price=500, **kwargs):
        return Product.objects.create(name=name, price=price, **kwargs)
    return make_product

@pytest.mark.django_db
def test_add_to_cart_and_view_cart(client, create_product):
    """
    1) Создать два товара через ORM.
    2) Зайти GET на список / (catalog:product_list) и убедиться, что товары там в контексте.
    3) Добавить один из товаров в корзину (POST на catalog:add_to_cart).
    4) Зайти GET на /cart/ и убедиться, что в корзине появился нужный товар с правильным количеством и ценой.
    """

    # 1) Создаём два товара
    p1 = create_product(name='Роза', price=300)
    p2 = create_product(name='Тюльпан', price=200)

    # 2) GET на / (список каталога)
    url_list = reverse('catalog:product_list')
    response_list = client.get(url_list)
    assert response_list.status_code == 200

    # Список товаров передаётся в response.context['products']
    products_in_context = set(response_list.context['products'])
    assert p1 in products_in_context and p2 in products_in_context

    # 3) Добавляем первый товар в корзину (POST → redirect)
    url_add = reverse('catalog:add_to_cart', args=[p1.id])
    response_add = client.post(url_add, data={'quantity': 2})
    # После успешного добавления — редирект на /cart/
    assert response_add.status_code == 302
    assert response_add.url == reverse('catalog:cart')

    # 4) GET на /cart/ и проверяем содержимое
    response_cart = client.get(reverse('catalog:cart'))
    assert response_cart.status_code == 200
    html = response_cart.content.decode('utf-8')

    # В HTML должно быть имя товара и количество «2»
    assert 'Роза' in html
    assert '2' in html

    # Проверяем итоговую сумму: 2 × 300 = 600 ₽
    assert '600' in html or '600.00' in html

    # 5) Добавляем второй товар с количеством 1
    url_add2 = reverse('catalog:add_to_cart', args=[p2.id])
    response_add2 = client.post(url_add2, data={'quantity': 1})
    assert response_add2.status_code == 302

    # Снова смотрим корзину
    response_cart2 = client.get(reverse('catalog:cart'))
    html2 = response_cart2.content.decode('utf-8')

    # Проверяем, что в корзине и «Тюльпан» появился, и сумма пересчиталась
    assert 'Тюльпан' in html2
    # Количество 1
    assert '1' in html2
    # Сумма теперь 600 + 200 = 800
    assert '800' in html2 or '800.00' in html2
