import pytest
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Product, Category

class BaseAPITestCase(APITestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.client = APIClient()
        # Создаём тестовые данные
        self.category = Category.objects.create(
            name="Electronics",
        )
        self.product = Product.objects.create(
            name="Laptop",
            price=999.99,
            quantity=10,
            category=self.category
        )

    @pytest.mark.django_db
    def tearDown(self):
        # Безопасное удаление только созданных в тесте объектов
        Product.objects.filter(id=self.product.id).delete()
        Category.objects.filter(id=self.category.id).delete()

class TestCategoryListView(BaseAPITestCase):
    @pytest.mark.django_db
    def test_get_categories_list_success(self):
        """Успешное получение списка категорий"""
        url = reverse('category-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Electronics')
        self.assertIn('description', response.data[0])

    @pytest.mark.django_db
    def test_get_empty_categories_list(self):
        """Получение пустого списка категорий"""
        Category.objects.all().delete()

        url = reverse('category-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class TestProductViewSet(BaseAPITestCase):
    @pytest.mark.django_db
    def test_list_products(self):
        """Получение списка продуктов"""
        url = reverse('product-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Laptop')
        self.assertAlmostEqual(float(response.data[0]['price']), 999.99, places=2)

    @pytest.mark.django_db
    def test_retrieve_product(self):
        """Получение конкретного продукта"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')
        self.assertAlmostEqual(float(response.data['price']), 999.99, places=2)
        self.assertEqual(response.data['quantity'], 10)
        self.assertEqual(response.data['category'], self.category.id)

    @pytest.mark.django_db
    def test_create_product_success(self):
        """Успешное создание продукта"""
        url = reverse('product-list')
        data = {
            'name': 'Mouse',
            'price': 29.99,
            'quantity': 50,
            'category': self.category.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Mouse')
        self.assertTrue(Product.objects.filter(name='Mouse').exists())

    @pytest.mark.django_db
    def test_create_product_invalid_name(self):
        """Тест: ошибка валидации при пустом name"""
        url = reverse('product-list')
        data = {
            'name': '',  # намеренно некорректное
            'price': 999.99,
            'quantity': 10,
            'category': self.category.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertEqual(
            response.data['name'][0].code,
            'blank'
        )

    @pytest.mark.django_db
    def test_create_product_invalid_price(self):
        """Тест: ошибка валидации при отрицательном price"""
        url = reverse('product-list')
        data = {
            'name': 'Phone',  # корректное имя
            'price': -10,  # намеренно некорректная цена
            'quantity': 5,
            'category': self.category.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    @pytest.mark.django_db
    def test_update_product(self):
        """Обновление продукта с корректными данными"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {
            'name': 'Updated Laptop',
            'price': 899.99,
            'quantity': 5,
            'category': self.category.id  # обязательно, если поле не nullable
            # image не передаём, если не обновляем
        }

        response = self.client.put(url, data, format='json')


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Laptop')
        self.assertEqual(float(response.data['price']), 899.99)

    @pytest.mark.django_db
    def test_partial_update_product(self):
        """Частичное обновление продукта"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})
        data = {'quantity': 5}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 5)
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.quantity, 5)

    @pytest.mark.django_db
    def test_delete_product(self):
        """Удаление продукта"""
        url = reverse('product-detail', kwargs={'pk': self.product.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    @pytest.mark.django_db
    def test_retrieve_nonexistent_product(self):
        """Попытка получить несуществующий продукт"""
        url = reverse('product-detail', kwargs={'pk': 9999})


        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestCategoryViewSet(BaseAPITestCase):
    @pytest.mark.django_db
    def test_list_categories(self):
        """Получение списка категорий"""
        url = reverse('category-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Electronics')

    @pytest.mark.django_db
    def test_retrieve_category(self):
        """Получение конкретной категории"""
        url = reverse('category-detail', kwargs={'pk': self.category.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

    @pytest.mark.django_db
    def test_create_category_success(self):
        """Успешное создание категории"""
        url = reverse('category-list')
        data = {
            'name': 'Books',
            'description': 'Literary works'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Books')
        self.assertTrue(Category.objects.filter(name='Books').exists())

    @pytest.mark.django_db
    def test_create_category_invalid_data(self):
        """Создание категории с некорректными данными"""
        url = reverse('category-list')
        data = {
            'name': '',  # пустое имя
            'description': 'Valid description'
        }

        response = self.client.post(url, data)