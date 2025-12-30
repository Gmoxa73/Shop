from rest_framework import serializers
from .models import Address, Contact

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city', 'street', 'house', 'building', 'structure', 'apartment']


class ContactSerializer(serializers.ModelSerializer):
    address = AddressSerializer()  # Вложенная структура

    class Meta:
        model = Contact
        fields = [
            'id', 'last_name', 'first_name', 'patronymic',
            'email', 'phone', 'address'
        ]

    def create(self, validated_data):
        # Извлекаем данные адреса
        address_data = validated_data.pop('address', None)
        contact = Contact.objects.create(**validated_data)

        if address_data:
            # Создаём адрес и связываем с контактом
            address = Address.objects.create(**address_data)
            contact.address = address
            contact.save()

        return contact