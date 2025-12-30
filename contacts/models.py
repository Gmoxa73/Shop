from django.db import models

class Address(models.Model):
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=20)
    building = models.CharField(max_length=10, blank=True)
    structure = models.CharField(max_length=10, blank=True)
    apartment = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.city}, {self.street}, {self.house}"


class Contact(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"