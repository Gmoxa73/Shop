from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'status'],
                condition=models.Q(status='active'),
                name='unique_active_cart_per_user'
            )
        ]

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
