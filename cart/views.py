from cacheops import cached_as
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product


class CartView(APIView):
    @cached_as(Cart.objects.all(), timeout=300)
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            status='active',
            defaults={'status': 'active'}
        )
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CartItemsView(APIView):
    @transaction.atomic
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity_str = request.data.get('quantity', '1')

        # Валидация и преобразование quantity
        try:
            quantity = int(quantity_str)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Quantity must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем или создаём корзину пользователя
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            status='active',
            defaults={'status': 'active'}
        )

        try:
            # Пытаемся получить существующий элемент корзины
            cart_item = CartItem.objects.select_for_update().get(
                cart=cart,
                product_id=product_id
            )
            # Только для существующего элемента: увеличиваем количество
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            # Для нового элемента: устанавливаем ровно то, что передали
            try:
                product = Product.objects.get(id=product_id)
                cart_item = CartItem.objects.create(
                    cart=cart,
            product=product,
            quantity=quantity,
            price=product.price
        )  # ← ЗАКРЫВАЮЩИЕ СКОБКИ ДОБАВЛЕНЫ
            except Product.DoesNotExist:
                return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemDetailView(APIView):
    def delete(self, request, item_id):
        try:
            # Проверяем, что CartItem принадлежит текущему пользователю
            cart_item = CartItem.objects.select_related('cart').get(
                pk=item_id,
                cart__user=request.user
            )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

class CartItemDeleteView(APIView):
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )