from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'created_at', 'total_amount', 'status', 'contact')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'contact__name')
    readonly_fields = ('created_at', 'total_amount')
    fieldsets = (
        ('Основная информация', {
            'fields': ('order_number', 'contact', 'created_at', 'shipping_date')
        }),
        ('Детали заказа', {
            'fields': ('total_amount', 'status')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__created_at',)
    search_fields = ('product__name', 'order__order_number')
    readonly_fields = ('total_price',)



