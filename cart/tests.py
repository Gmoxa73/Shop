import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Cart, CartItem, Product

TEST_PASSWORD = 'testpass123'

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_fixture():
    user = User.objects.create_user(
        username='22',
        email='22@example.com',
        password=TEST_PASSWORD,
        first_name='sssss',
        last_name='sssss',
        is_active=True
    )
    yield user
    user.delete()

@pytest.fixture
def authorized_api_client(api_client, user_fixture):
    login_url = reverse('login')
    login_data = {'email': user_fixture.email, 'password': TEST_PASSWORD}
    response = api_client.post(login_url, data=login_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    token = response.data.get('token')
    assert token is not None
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.mark.django_db
def test_cart_view_unauthenticated(api_client):
    """Тест: GET-запрос без авторизации должен возвращать 401"""
    url = reverse('cart') 
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'error' in response.data
    assert 'Authentication required' in response.data['error']


@pytest.mark.django_db
def test_add_item_to_cart_success(authorized_api_client, product_fixture, cart_fixture):
    url = reverse('cart-item')
    data = {
        'product_id': product_fixture.id,
        'quantity': 1
    }

    response = authorized_api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED




