from rest_framework import serializers

from shared.models import CustomField
from .models import Product, Category


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = ['key', 'value']


class ProductSerializer(serializers.ModelSerializer):
    custom_fields = CustomFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  # или перечислите нужные поля