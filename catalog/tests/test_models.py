import pytest
from django.core.exceptions import ValidationError
from catalog.models import Product

@pytest.mark.django_db
def test_product_str(product1):
    """
    __str__ для Product должен возвращать его name.
    """
    assert str(product1) == "Роза"

@pytest.mark.django_db
def test_negative_price_raises_validation_error():
    """
    Попытка сохранить продукт с отрицательной ценой
    должна падать ValidationError при full_clean().
    """
    product = Product(name="Тестовый", price=-100)
    with pytest.raises(ValidationError):
        product.full_clean()
