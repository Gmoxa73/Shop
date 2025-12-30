from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        if not obj.cart:
            return []  # или другое значение по умолчанию
        cart_items = obj.cart.items.all()
        return [
            {
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.price
            }
            for item in cart_items
        ]

    class Meta:
        model = Order
        fields = ['order_number', 'created_at', 'total_amount', 'status', 'items']