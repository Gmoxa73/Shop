import os
import django
# Инициализация Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Store_api.settings'
django.setup()
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User



@pytest.fixture
def api_client():
    """Фикстура для создания экземпляра APIClient"""
    return APIClient()


@pytest.fixture
def user_fixture():
    """Фикстура для создания тестового пользователя"""
    user = User.objects.create_user(
        username='222',
        email='222@example.com',
        password='strong_password456',
        is_active=True
    )
    yield user
    user.delete()

@pytest.fixture
def authorized_api_client(api_client, user_fixture):
    """Фикстура для авторизованного клиента"""
    login_url = reverse('login')
    login_data = {
        'email': user_fixture.email,
        'password': user_fixture.password,
    }

    print(f"DEBUG: Sending login data: {login_data}")
    response = api_client.post(login_url, data=login_data, format='json')
    print(f"DEBUG: Response status: {response.status_code}")
    print(f"DEBUG: Response data: {response.data}")

    assert response.status_code == status.HTTP_200_OK, (
        f"Login failed: {response.status_code} - {response.data}. "
        f"Sent: {login_data}"
    )

    token = response.data.get('token')
    assert token is not None, "Token not found in login response"

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


#Тестовые функции
@pytest.mark.django_db
def test_user_creation(user_fixture):
    """Тест создания пользователя"""
    assert user_fixture is not None
    assert user_fixture.username == '222'
    assert user_fixture.email == '222@example.com'
    assert user_fixture.is_active is True

@pytest.mark.django_db
def test_user_registration(api_client):
    register_url = reverse('register')
    register_data = {
        "email": "222@example.com",
        "password": "strong_password456",
        "first_name": "Vasya",
        "last_name": "Vassya",
    }
    response = api_client.post(register_url, data=register_data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_login_api(api_client, user_fixture):
    register_url = reverse('register')
    register_data = {
        "email": user_fixture.email,
        "password": user_fixture.password,
        "first_name": "Vasya",
        "last_name": "Vassya",
    }
    response = api_client.post(register_url, data=register_data, format='json')
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED

    """Тест POST-запроса на авторизацию"""
    login_url = reverse('login')
    print(f"DEBUG: Sending login data: {login_url}")
    login_data = {
        "email": user_fixture.email,
        "password": user_fixture.password,
    }
    response = api_client.post(login_url, login_data, format='json')

    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")

    assert response.status_code == status.HTTP_200_OK, (
        f"Авторизация не прошла: {response.status_code} - {response.data}"
    )
    assert 'token' in response.data, "В ответе отсутствует токен авторизации"
    assert 'user' in response.data, "В ответе отсутствует информация о пользователе"
    user_data = response.data['user']
    assert user_data['email'] == login_data['email'], "Email в ответе не совпадает с отправленным"