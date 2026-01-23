import pytest
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from products.models import Category
from .models import Product, Cart




@pytest.fixture
def api_client():
    """Фикстура для создания DRF APIClient"""
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
def category_fixture():
    category = Category.objects.create(name='Test Category')
    yield category
    category.delete()

@pytest.fixture
def product_fixture(category_fixture):
    product = Product.objects.create(
        category=category_fixture,
        name='Test Product',
        price=100.0,
        quantity=10,
        image='products/test_image.jpg'
    )
    yield product
    product.delete()

@pytest.fixture
def cart_fixture(user_fixture):
    cart = Cart.objects.create(user=user_fixture)
    yield cart
    cart.delete()


@pytest.fixture
def authorized_api_client(api_client, user_fixture):
    """Фикстура авторизованного API-клиента"""
    # Логинимся и получаем токен
    login_url = reverse('login')
    login_data = {
        'email': user_fixture.email,
        'password': 'testpass123'
    }
    response = api_client.post(login_url, data=login_data, format='json')

    assert response.status_code == status.HTTP_200_OK
    token = response.data.get('token')
    assert token is not None

    # Устанавливаем заголовок авторизации
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client