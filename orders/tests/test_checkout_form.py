import pytest
from django.utils import timezone
from datetime import timedelta
from orders.views import CheckoutForm

@pytest.mark.django_db
def test_checkout_form_valid():
    """
    Проверяем, что форма валидна для даты-завтра, валидного времени и адреса.
    """
    tomorrow = timezone.localdate() + timedelta(days=1)
    form_data = {
        'delivery_date':    tomorrow,
        'delivery_time':    '14:30',
        'delivery_address': 'пр. Мира, д.5',
    }
    form = CheckoutForm(data=form_data)
    assert form.is_valid(), form.errors

@pytest.mark.django_db
def test_checkout_form_missing_fields():
    """
    Если никакие поля не переданы — все три поля должны выдать ошибки required.
    """
    form = CheckoutForm(data={})
    assert not form.is_valid()
    assert set(form.errors.keys()) == {'delivery_date', 'delivery_time', 'delivery_address'}

@pytest.mark.django_db
def test_checkout_form_past_date_invalid():
    """
    Дата в прошлом (сегодня и ранее) недопустима.
    """
    yesterday = timezone.localdate() - timedelta(days=1)
    form_data = {
        'delivery_date':    yesterday,
        'delivery_time':    '10:00',
        'delivery_address': 'ул. Безымянная, д.1',
    }
    form = CheckoutForm(data=form_data)
    assert not form.is_valid()
    assert 'delivery_date' in form.errors
