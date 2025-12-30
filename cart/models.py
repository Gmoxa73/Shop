from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True  # добавлен индекс
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_amount(self):
        """Общая сумма товаров в корзине."""
        return sum(item.price * item.quantity for item in self.items.all())

    def __str__(self):
        if self.user:
            return f'Корзина пользователя {self.user.username}'
        return f'Гостевая корзина {self.id}'

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['cart', 'product']),  # индекс по корзине + товару
            models.Index(fields=['product']),  # индекс по товару
        ]

    def __str__(self):
        product_name = self.product.name if self.product else "Неизвестный товар"
        return f'{product_name} ({self.quantity} шт.)'
