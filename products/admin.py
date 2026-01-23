
from django.contrib import admin
from .models import Category, Product, ProductParameter

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1
    fields = ('key', 'value')
    verbose_name = 'Характеристика'
    verbose_name_plural = 'Характеристики'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'category',]  # ← shop отсутствует в модели
    list_filter = ['category', ]  # ← shop отсутствует в модели
