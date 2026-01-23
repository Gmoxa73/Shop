import pytest
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Cart, CartItem
from products.models import Product
from products.models import Category
import json

class CartViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # ← принудительная авторизация

        Cart.objects.filter(user=self.user).delete()
        CartItem.objects.filter(cart__user=self.user).delete()

    def test_get_cart_authenticated_new_cart(self):
        response = self.client.get('/api/v1/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 0,
                  "New cart should have no items")

    @pytest.mark.django_db
    def test_get_cart_authenticated_new_cart(self):
        response = self.client.get('/api/v1/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 0,
                         "New cart should have no items")

class CartAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cart = Cart.objects.create(user=self.user, status='active')

        # Очистка: удаляем все корзины и элементы корзины пользователя
        Cart.objects.filter(user=self.user).delete()
        CartItem.objects.filter(cart__user=self.user).delete()

        # Создаём категорию
        self.category = Category.objects.create(
            name='Test Category'
        )

        # Создаём товар С ОБЯЗАТЕЛЬНЫМ category
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            quantity=10,
            category=self.category  # ← обязательно!
        )

        # Далее создаём корзину и элемент корзины
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
    def tearDown(self):
        # Дополнительная очистка после теста
        CartItem.objects.all().delete()
        Cart.objects.all().delete()

    @pytest.mark.django_db
    def test_get_cart_unauthenticated(self):
        """Тест: получение корзины без аутентификации"""
        self.client.logout()
        response = self.client.get('/api/v1/cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)



    @pytest.mark.django_db
    def test_get_cart_authenticated_existing_cart(self):
        Cart.objects.filter(user=self.user, status='active').delete()  # очистка
        cart = Cart.objects.create(user=self.user, status='active')

        response = self.client.get('/api/v1/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], cart.id)

    @pytest.mark.django_db
    def test_add_item_to_cart(self):
        url = '/api/v1/cart/items/'
        response = self.client.post(url, {
            'product_id': self.product.id,
            'quantity': 2
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 3)
        self.assertIn('product_name', response.data)

    @pytest.mark.django_db
    def test_add_existing_item_increases_quantity(self):
        # Сначала добавляем товар
        self.client.post('/api/v1/cart/items/', {
            'product_id': self.product.id,
            'quantity': 1
        })

    @pytest.mark.django_db
    def test_create_new_cart_item(self):
        response = self.client.post('/api/v1/cart/items/', {
            'product_id': self.product.id,
            'quantity': 5
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 6)

    class CartItemsViewTestCase(APITestCase):
        def setUp(self):
            # Гарантируем чистоту БД перед каждым тестом
            CartItem.objects.all().delete()
            Cart.objects.all().delete()

            self.user = User.objects.create_user(
                username='testuser',
                password='testpass'
            )
            self.client = APIClient()
            self.client.force_authenticate(user=self.user)
            self.cart = Cart.objects.create(user=self.user, status='active')

            # Создаём категорию и продукт
            self.category = Category.objects.create(name='Electronics')
            self.product = Product.objects.create(
                name='Test Product',
                price=100,
                quantity=10,
                category=self.category
            )

        def tearDown(self):
            # Дополнительная очистка
            CartItem.objects.all().delete()
            Cart.objects.all().delete()



    @pytest.mark.django_db
    def test_delete_cart_item(self):
        """Тест: удаление существующего элемента корзины."""
        # Сначала создаём CartItem
        create_response = self.client.post('/api/v1/cart/items/', {
            'product_id': self.product.id,
            'quantity': 1
        })
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        item_id = create_response.data['id']

        # Теперь пытаемся удалить
        delete_response = self.client.delete(f'/api/v1/cart/delete/{item_id}/')
        print("Delete response status:", delete_response.status_code)  # ← диагностика
        print("Delete response data:", delete_response.data)  # ← диагностика

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Дополнительная проверка: элемент действительно удалён
        with self.assertRaises(CartItem.DoesNotExist):
            CartItem.objects.get(id=item_id)

class CartItemDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cart = Cart.objects.create(user=self.user, status='active')

        # Создаём категорию
        self.category = Category.objects.create(name='Electronics')

        # Указываем категорию при создании продукта
        self.product = Product.objects.create(
            name='Test Product',
            price=100,
            quantity=10,
            category=self.category
        )


    @pytest.mark.django_db
    def test_delete_other_users_item(self):
        """Тест: попытка удалить товар другого пользователя"""
        other_user = User.objects.create_user(username='otheruser', password='pass')
        other_cart = Cart.objects.create(user=other_user)
        other_item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=1,
            price=self.product.price
        )

        response = self.client.delete(f'/api/v1/cart/items/{other_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)