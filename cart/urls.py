from django.urls import path
from .views import CartView, CartItemsView, CartItemDetailView, CartItemDeleteView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/', CartItemsView.as_view(), name='cart-items'),
    path('cart/items/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('cart/delete/<int:item_id>/', CartItemDeleteView.as_view(), name='cart-item-delete'),
]
