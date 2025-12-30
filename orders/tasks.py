from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmation(order_id):
    try:
        order = Order.objects.get(id=order_id)
        send_mail(
            'Подтверждение заказа',
            f'Ваш заказ #{order.id} принят!',
            'noreply@store.com',
            [order.user_email],
        )
    except Order.DoesNotExist:
        pass

@shared_task
def send_admin_invoice(order_id):
    send_mail(
        'Новая накладная для обработки',
        f'Требуется обработать заказ #{order_id}',
        'noreply@store.com',
        ['admin@store.com'],
    )