from django.db import models

class Category(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    model = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='products/')
    name = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    shop = models.CharField(max_length=100, default='Связной')

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameters')
    key = models.CharField(max_length=100)  # название характеристики
    value = models.TextField()  # значение (может быть числом, строкой, булевым)

    class Meta:
        unique_together = ('product', 'key')