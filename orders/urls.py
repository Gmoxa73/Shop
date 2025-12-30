# Инициализируем роутер
from django.urls import path
from . import views

urlpatterns = [
    path('orders/confirm/', views.OrderConfirmView.as_view(), name='order-confirm'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<str:order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<str:order_number>/', views.OrderDetailView.as_view(),
     {'put': 'update_status'}, name='order-update'),
    path('orders/from-cart/<int:cart_id>/', views.CreateOrderFromCart.as_view(), name='create-order-from-cart'),
]