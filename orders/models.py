from django.db import models
from uuid import uuid4
from decimal import Decimal
from cart.models import Cart
from contacts.models import Contact
from products.models import Product
from django.core.validators import MinValueValidator


def generate_short_uuid():
    return uuid4().hex[:8]


class Order(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    order_number = models.CharField(
        max_length=20,
        default=generate_short_uuid,
        unique=True,
        db_index=True
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Корзина, из которой создан заказ (может быть очищена после оформления)"
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        help_text="Контакт покупателя",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True
    )
    shipping_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.order_number

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        help_text="Товар, который был в заказе",
        null=True,
        blank=True
    )
    # product_name можно оставить как кэшированное поле или убрать
    product_name = models.CharField(max_length=100, blank=True, default='')
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Количество товара в заказе"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена на момент создания заказа"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal('0.00'),
        help_text="Общая стоимость позиции (quantity × price)"
    )

    def save(self, *args, **kwargs):
        # Обновляем product_name и total_price перед сохранением
        if self.product and not self.product_name:
            self.product_name = self.product.name
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} × {self.product_name} ({self.price})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_order_product'
            )
        ]


