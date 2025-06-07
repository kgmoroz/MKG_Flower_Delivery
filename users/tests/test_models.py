import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_get_full_name_returns_first_and_last(user):
    # для пользователя с first_name='Иван', last_name='Петров'
    assert user.get_full_name() == "Иван Петров"

@pytest.mark.django_db
def test_get_full_name_falls_back_to_username(user_no_name):
    # если имя не задано — get_full_name возвращает пустую строку,
    # и мы в уведомлениях используем username
    assert user_no_name.get_full_name() == ""

@pytest.mark.django_db
def test_str_returns_username(user):
    # __str__ у CustomUser по умолчанию выводит username
    assert str(user) == user.username
