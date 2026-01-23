import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Contact, Address


@pytest.fixture
def api_client():
    """Фикстура для DRF APIClient"""
    return APIClient()


@pytest.fixture
def address_fixture(db):
    address = Address.objects.create(
        city="Москва",
        street="Тверская",
        house="1"
    )
    yield address
    address.delete()

@pytest.fixture
def contact_fixture(db, address_fixture):
    contact = Contact.objects.create(
        first_name="Иван",
        last_name="Петров",
        email="ivan@example.com",
        phone="+79991234567",
        address=address_fixture
    )
    yield contact
    contact.delete()

class TestContactCreateView:
    @pytest.mark.django_db
    def test_create_contact_success(self, api_client):
        url = reverse("contact-create")  # соответствует urls.py
        data = {
            "first_name": "Анна",
            "last_name": "Сидорова",
            "email": "anna@example.com",
            "phone": "+79997654321",
            "address": {
                "city": "Санкт-Петербург",
                "street": "Невский",
                "house": "10"
            }
        }
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}: {response.data}"
        assert response.data["first_name"] == "Анна"
        assert "id" in response.data

    @pytest.mark.django_db
    def test_create_contact_invalid_data(self, api_client):
        url = reverse("contact-create")
        data = {
            "first_name": "",
            "last_name": "Иванов",
            "email": "invalid-email",
            "phone": "+79991234567"
        }
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}"
        assert "first_name" in response.data
        assert "email" in response.data

class TestContactFilteredListView:
    """Тесты для ContactFilteredListView (GET /api/contacts/)"""

    @pytest.mark.django_db
    def test_get_contacts_list_success(self, api_client, contact_fixture):
        """Получение списка контактов"""
        url = reverse("contact-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert contact_fixture.first_name in [c["first_name"] for c in response.data]

    @pytest.mark.django_db
    def test_filter_by_city(self, api_client, contact_fixture, address_fixture):
        """Фильтрация контактов по городу"""
        url = reverse("contact-list") + "?city=Москва"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        for contact in response.data:
            assert contact["address"]["city"] == "Москва"

    @pytest.mark.django_db
    def test_search_by_name(self, api_client, contact_fixture):
        """Поиск контактов по имени/фамилии"""
        url = reverse("contact-list") + "?search=Иван"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        for contact in response.data:
            assert "Иван" in contact["first_name"] or "Иван" in contact["last_name"]

    @pytest.mark.django_db
    def test_search_by_email(self, api_client, contact_fixture):
        """Поиск контактов по email"""
        url = reverse("contact-list") + "?search=ivan@example.com"


        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        for contact in response.data:
            assert "ivan@example.com" in contact["email"]

    @pytest.mark.django_db
    def test_empty_filter_results(self, api_client):
        """Пустой результат при отсутствии данных"""
        url = reverse("contact-list") + "?city=Новосибирск"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    @pytest.mark.django_db
    def test_no_filter_params(self, api_client, contact_fixture):
        """Запрос без параметров фильтрации"""
        url = reverse("contact-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
