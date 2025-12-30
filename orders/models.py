from django.db import models
from uuid import uuid4

from cart.models import Cart


def generate_short_uuid():
    return uuid4().hex[:8]

class Order(models.Model):
    order_number = models.CharField(max_length=20,  default=generate_short_uuid)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='pending')
    shipping_date = models.DateTimeField(null=True, blank=True)
    contact_id = models.IntegerField(default=1)

    def __str__(self):
        return self.order_number



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, default=1)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)