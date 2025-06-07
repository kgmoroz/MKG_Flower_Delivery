import pytest
from django.contrib.auth import get_user_model
from users.forms import CustomUserCreationForm

User = get_user_model()

@pytest.mark.django_db
def test_custom_user_creation_form_valid():
    """
    При корректных данных форма валидна и создаёт пользователя.
    """
    form_data = {
        'username':   'newuser',
        'email':      'new@example.com',
        'first_name': 'Пётр',
        'last_name':  'Иванов',
        'phone':      '+7-123-456-78-90',
        'address':    'ул. Ленина, д.1',
        'password1':  'ComplexPass123',
        'password2':  'ComplexPass123',
    }
    form = CustomUserCreationForm(data=form_data)
    assert form.is_valid(), form.errors
    user = form.save()
    # пользователь действительно в базе
    assert User.objects.filter(pk=user.pk, email='new@example.com').exists()

@pytest.mark.django_db
def test_custom_user_creation_form_password_mismatch():
    """
    Если пароли не совпадают — форма не валидна, и есть ошибка по полю password2.
    """
    form_data = {
        'username':  'newuser2',
        'email':     'new2@example.com',
        'phone':     '+7-111-111-11-11',
        'address':   'ул. Пушкина, д.10',
        'password1': 'Pass12345',
        'password2': 'WrongPass',
    }
    form = CustomUserCreationForm(data=form_data)
    assert not form.is_valid()
    assert 'password2' in form.errors
