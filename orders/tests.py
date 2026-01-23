import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from contacts.models import Contact
from products.models import Product, Category


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def contact_fixture():
    contact = Contact.objects.create(
        last_name="Test",
        first_name="User",
        email="test@example.com"
    )
    yield contact
    # Очистка: сначала связанные заказы
    Order.objects.filter(contact=contact).delete()
    # Потом сам контакт
    contact.delete()

@pytest.fixture
def category_fixture(db):
    category = Category.objects.create(name="Электроника")
    yield category
    category.delete()

@pytest.fixture
def product_fixture(db, category_fixture):
    product = Product.objects.create(
        name="Тестовый товар",
        price=1000.0,
        quantity=10,
        category=category_fixture
    )
    yield product
    product.delete()


@pytest.fixture
def cart_fixture():
    user = User.objects.create_user(
        username='testuser',
        password='testpass'
    )
    cart = Cart.objects.create(
        user=user,
        status='active'
    )
    return cart


@pytest.fixture
def cart_with_items_fixture(db, cart_fixture, product_fixture):
    item = CartItem.objects.create(
        cart=cart_fixture,
        product=product_fixture,
        quantity=2,
        price=1000.0
    )
    yield cart_fixture
    item.delete()


@pytest.fixture
def order_fixture(db, contact_fixture):
    order = Order.objects.create(
        contact=contact_fixture,
        status="pending",
        total_amount=2000.0
    )
    yield order
    order.delete()

class TestOrderConfirmView:
    @pytest.mark.django_db
    def test_create_order_success(self, api_client, cart_with_items_fixture, contact_fixture):
        url = reverse("order-confirm")
        data = {
            "cart_id": cart_with_items_fixture.id,
            "contact_id": contact_fixture.id
        }
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "order_number" in response.data

    @pytest.mark.django_db
    def test_invalid_cart_or_contact_id(self, api_client):
        url = reverse("order-confirm")
        data = {"cart_id": "invalid", "contact_id": "invalid"}
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_missing_cart_or_contact_id(self, api_client):
        url = reverse("order-confirm")
        data = {"cart_id": 1}  # отсутствует contact_id
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    @pytest.mark.django_db
    def test_cart_not_found(self, api_client, contact_fixture):
        url = reverse("order-confirm")
        data = {"cart_id": 9999, "contact_id": contact_fixture.id}
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestOrderListView:
    @pytest.mark.django_db
    def test_get_orders_list_success(self, api_client, order_fixture):
        url = reverse("orders-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

class TestOrderConfirmView:
    """Тесты для OrderConfirmView (POST /api/orders/confirm/)"""

    @pytest.mark.django_db
    def test_get_order_detail_success(self, api_client, order_fixture):
        url = reverse("order-detail", kwargs={"order_number": order_fixture.order_number})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_order_not_found(self, api_client):
        url = reverse("order-detail", kwargs={"order_number": "NON-EXISTENT"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_invalid_cart_or_contact_id(self, api_client):
        """Ошибка при некорректных cart_id или contact_id"""
        url = reverse("order-confirm")
        data = {
            "cart_id": "invalid",
            "contact_id": "invalid"
        }

        response = api_client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    @pytest.mark.django_db
    def test_missing_cart_or_contact_id(self, api_client):
        """Ошибка при отсутствии cart_id или contact_id"""
        url = reverse("order-confirm")
        data = {"cart_id": 1}  # отсутствует contact_id

        response = api_client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    @pytest.mark.django_db
    def test_cart_not_found(self, api_client, contact_fixture):
        """Ошибка при несуществующей корзине"""
        url = reverse("order-confirm")
        data = {
            "cart_id": 9999,  # несуществующий ID
            "contact_id": contact_fixture.id
        }

        response = api_client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data

class TestOrderListView:
    """Тесты для OrderListView (GET /api/orders/)"""

    @pytest.mark.django_db
    def test_get_orders_list_success(self, api_client, order_fixture):
        """Получение списка заказов"""
        url = reverse("order-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert order_fixture.order_number in [o["order_number"] for o in response.data]

class TestOrderDetailView:
    """Тесты для OrderDetailView"""

    @pytest.mark.django_db
    def test_get_order_detail_success(self, api_client, order_fixture):
        """Получение конкретного заказа"""
        url = reverse("order-detail", kwargs={"order_number": order_fixture.order_number})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["order_number"] == order_fixture.order_number

    @pytest.mark.django_db
    def test_order_not_found(self, api_client):
        """Ошибка при поиске несуществующего заказа"""
        url = reverse("order-detail", kwargs={"order_number": "NON-EXISTENT"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data

    @pytest.mark.django_db
    def test_update_order_status(self, api_client, order_fixture):
        """Обновление статуса заказа"""
        url = reverse("order-detail", kwargs={"order_number": order_fixture.order_number})
        data = {"status": "shipped"}
        response = api_client.put(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "shipped"
        updated_order = Order.objects.get(order_number=order_fixture.order_number)
        assert updated_order.shipping_date is not None

    @pytest.mark.django_db
    def test_update_invalid_status(self, api_client, order_fixture):
        """Попытка обновить статус несуществующего заказа"""
        url = reverse("order-detail", kwargs={"order_number": "INVALID-ORDER"})
        data = {"status": "shipped"}
        response = api_client.put(url, data=data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_order_from_cart_success(self, api_client, cart_with_items_fixture, contact_fixture):
        """Успешное создание заказа из корзины"""
        url = reverse("create-order-from-cart", kwargs={"cart_id": cart_with_items_fixture.id})
        data = {"contact_id": contact_fixture.id}
        response = api_client.post(url, data=data, format="json")

        # Проверка статуса
        assert response.status_code == status.HTTP_201_CREATED
        # Проверка полей ответа
        assert "order_number" in response.data
        # Проверка суммы с преобразованием и округлением
        assert pytest.approx(float(response.data["total_amount"]), 0.01) == 2000.0
        assert response.data["status"] == "pending"
        # Проверка существования заказа в БД
        assert Order.objects.filter(order_number=response.data["order_number"]).exists()


    def tearDown(self):
        """Очистка БД после тестов"""
        Order.objects.all().delete()
        Contact.objects.all().delete()
        Cart.objects.all().delete()

@pytest.mark.django_db
def test_create_order_missing_contact_id(api_client, cart_with_items_fixture):
    """Ошибка при отсутствии contact_id"""
    url = reverse("create-order-from-cart", kwargs={"cart_id": cart_with_items_fixture.id})
    data = {}  # contact_id отсутствует

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert "contact_id обязателен" in str(response.data["error"])

@pytest.mark.django_db
def test_create_order_invalid_cart_id(api_client, contact_fixture):
    invalid_cart_id = 9999  # ID, которого нет в БД
    url = reverse("create-order-from-cart", kwargs={"cart_id": invalid_cart_id})
    response = api_client.post(url, {"contact_id": contact_fixture.id})
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_create_order_cart_not_found(api_client, contact_fixture):
    """Ошибка при несуществующей корзине"""
    non_existent_cart_id = 9999
    url = reverse("create-order-from-cart", kwargs={"cart_id": non_existent_cart_id})
    data = {"contact_id": contact_fixture.id}
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data
    assert "Корзина не найдена" in str(response.data["error"])


@pytest.mark.django_db
def test_create_order_success(api_client, cart_with_items_fixture, contact_fixture):
    url = reverse("create-order-from-cart", kwargs={"cart_id": cart_with_items_fixture.id})
    response = api_client.post(url, {"contact_id": contact_fixture.id})
    assert response.status_code == status.HTTP_201_CREATED
