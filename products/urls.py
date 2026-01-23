from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, CategoryListView

# Создаём роутер и регистрируем ViewSet
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

# Основные URL
urlpatterns = [
    # Маршруты от роутера (полный CRUD для products и categories)
    path('', include(router.urls)),

    # Отдельный endpoint для списка категорий (только чтение)
    path('categories/', CategoryListView.as_view(), name='category-list'),
]