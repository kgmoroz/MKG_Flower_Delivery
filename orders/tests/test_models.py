import pytest

@pytest.mark.django_db
def test_order_items_relationship(order, product1, product2):
    """
    У заказа из фикстуры должно быть ровно 2 позиции
    и они должны соответствовать product1 и product2.
    """
    items = list(order.items.all())
    assert len(items) == 2

    names = {item.product.name for item in items}
    assert names == {"Роза", "Лилия"}


@pytest.mark.django_db
def test_order_total_amount_method(order):
    """
    Проверяем, что метод total_amount() (или свойство)
    корректно суммирует: 2×500 + 1×700 = 1700.
    """
    # если в модели реализован метод total_amount()
    assert order.total_amount() == 2 * 500 + 1 * 700

    # если это свойство order.total_amount
    # assert order.total_amount == 1700
