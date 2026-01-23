
from rest_framework import serializers
from .models import Contact, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    address = AddressSerializer()  # вложенный сериализатор

    class Meta:
        model = Contact
        fields = '__all__'

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            address = Address.objects.create(**address_data)
            validated_data['address'] = address
        contact = Contact.objects.create(**validated_data)
        return contact

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data and instance.address:
            address_serializer = AddressSerializer(
                instance.address,
                data=address_data
            )
            if address_serializer.is_valid():
                address_serializer.save()
        elif address_data:
            Address.objects.create(
                **address_data,
                contact=instance
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance