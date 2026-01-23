from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer
import uuid
from django.utils import timezone
from .tasks import send_order_confirmation, send_admin_invoice  # импорт задачи Celery
import logging

logger = logging.getLogger(__name__)

class OrderConfirmView(APIView):
    def post(self, request):
        try:
            cart_id = int(request.data.get('cart_id'))
            contact_id = int(request.data.get('contact_id'))
        except (ValueError, TypeError):
            return Response(
                {"error": "cart_id и contact_id должны быть числами"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not cart_id or not contact_id:
            return Response(
                {'error': 'cart_id и contact_id обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Получаем корзину и товары
            cart = Cart.objects.get(id=cart_id)
            total_amount = cart.total_amount

            # Создаем заказ
            order = Order.objects.create(
                order_number=f"ORD-{timezone.now().year}-{uuid.uuid4().hex[:5].upper()}",
                created_at=timezone.now(),
                total_amount=total_amount,
                status='pending',
                cart_id=cart_id,
                contact_id=contact_id
            )

            # Сохраняем позиции заказа
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.price
                )

            # ВЫЗОВ CELERY-ЗАДАЧ
            send_order_confirmation.delay(order_id=order.id)
            send_admin_invoice.delay(order_id=order.id)

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response(
                {"error": "Корзина не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return Response(
                {"error": "Произошла ошибка при создании заказа"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderDetailView(APIView):
    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
            new_status = request.data.get('status')
            if new_status:
                order.status = new_status
                if new_status == 'shipped':
                    order.shipping_date = datetime.now()
                order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

class CreateOrderFromCart(APIView):
    def post(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            if not isinstance(cart_id, int) or cart_id <= 0:
                return Response({'error': 'Неверный cart_id'}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Корзина не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Рассчитываем общую сумму
        try:
            total_amount = sum(item.price * item.quantity for item in cart.items.all())
        except (TypeError, ValueError) as e:
            return Response({'error': f'Ошибка расчёта суммы: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response({'error': 'contact_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        # Создаем заказ
        order = Order.objects.create(
            order_number=f"ORD-{timezone.now().year}-{uuid.uuid4().hex[:5].upper()}",
            created_at=timezone.now(),
            total_amount=total_amount,
            status='pending',
            cart=cart,
            contact_id=request.data.get('contact_id')  # ID контакта из запроса
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)