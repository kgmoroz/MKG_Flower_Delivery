import pytest
from django.urls import reverse
from django.test import Client

from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_user_registration_and_login_flow(client):
    """
    1) На GET /accounts/signup/ получить форму регистрации (200).
    2) Отправить POST на /accounts/signup/ с валидными данными.
       Убедиться, что происходит редирект на product_list.
    3) Проверить в базе: пользователь создан и у него задане поле username/email и т. д.
    4) После регистрации пользователь должен быть уже залогинен (client.session содержит user_id).
    5) Выйти (GET или POST на /accounts/logout/) и убедиться, что после редиректа
       при GET /accounts/login/ форма появляется (200).
    6) Войти через client.post('/accounts/login/', …) с теми же данными, проверить
       редирект, и что session снова содержит user_id.
    """

    # 1) GET на форму регистрации
    url_signup = reverse('users:signup')
    response_get = client.get(url_signup)
    assert response_get.status_code == 200
    # Форма должна содержать input name="username", name="password1", name="password2" и т. п.
    content = response_get.content.decode('utf-8')
    assert 'name="username"' in content
    assert 'name="password1"' in content
    assert 'name="password2"' in content

    # 2) Отправляем POST с валидными данными
    form_data = {
        'username':   'bob',
        'password1':  'verysecure123',
        'password2':  'verysecure123',
        'email':      'bob@example.com',
        # Если в вашей форме есть дополнительные поля (например,
        # first_name, last_name, address, phone), добавьте и их сюда с валидными значениями.
        # Например: 'first_name': 'Bob', 'last_name': 'Builder',
    }
    response_post = client.post(url_signup, data=form_data)
    # После успешной регистрации по коду должно быть перенаправление (302)
    assert response_post.status_code == 302
    # На какой URL должен быть редирект? Мы в signup_view после успешного login() делаем redirect('catalog:product_list')
    expected_url = reverse('catalog:product_list')
    assert response_post.url == expected_url

    # 3) Проверяем, что пользователь создан в базе
    user = User.objects.filter(username='bob').first()
    assert user is not None
    assert user.email == 'bob@example.com'

    # 4) После регистрации клиентская сессия уже должна быть аутентифицирована
    # Django хранит user_id в request.session['_auth_user_id']
    session = client.session
    assert session.get('_auth_user_id') is not None

    # 5) Выходим из системы
    url_logout = reverse('logout')
    response_logout = client.get(url_logout)
    # В вашей настройке LogoutView отрисовывает страницу «logged_out.html» (200),
    # поэтому проверяем именно 200, а не редирект
    assert response_logout.status_code == 200

    # Теперь GET /accounts/login/ должен вернуть форму
    url_login = reverse('login')
    response_login_get = client.get(url_login)
    assert response_login_get.status_code == 200
    content_login = response_login_get.content.decode('utf-8')
    assert 'name="username"' in content_login
    assert 'name="password"' in content_login

    # 6) Пробуем снова войти
    login_data = {
        'username': 'bob',
        'password': 'verysecure123',
    }
    response_login_post = client.post(url_login, data=login_data)
    # При удачном логине Django по умолчанию делает редирект на settings.LOGIN_REDIRECT_URL или '/'
    assert response_login_post.status_code == 302
    # Проверим, что после повторного входа в сессии снова есть _auth_user_id
    session2 = client.session
    assert session2.get('_auth_user_id') == str(user.id)
