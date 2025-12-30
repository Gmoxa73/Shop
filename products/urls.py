from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, CategoryListView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('products/', ProductViewSet.as_view({'get': 'list'}), name='product-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
]