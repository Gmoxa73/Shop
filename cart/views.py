from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product


class CartView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required. Please provide a valid token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
            cart = Cart.objects.get(user=request.user)
        except (Product.DoesNotExist, Cart.DoesNotExist):
            return Response({'error': 'Продукт или корзина не найдены'}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли уже такой товар в корзине
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                price=product.price
            )

        cart_item.save()
        return Response({'message': 'Товар добавлен в корзину'}, status=status.HTTP_201_CREATED)

    def delete(self, request, item_id):
        # print(f"Пытаемся удалить item_id={item_id}, user={request.user}")  # Отладка
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            return Response({'message': f'Товар {item_id} удалён из корзины'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Элемент корзины не найден'}, status=status.HTTP_404_NOT_FOUND)