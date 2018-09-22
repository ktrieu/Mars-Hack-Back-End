"""
Definition of models.
"""

from django.db import models
from django.contrib import admin

class User(models.Model):
    
    customer_id = models.CharField(max_length=73, unique=True)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10)

    income = models.IntegerField()

    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)

    order_range_km = models.IntegerField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

admin.site.register(User)

class Product(models.Model):

    store = models.CharField(max_length=30)
    name = models.CharField(max_length=30)

    price = models.DecimalField(max_digits=5, decimal_places=2)

    description = models.TextField()

    image_url = models.URLField()

    def __str__(self):
        return self.name

admin.site.register(Product)

class OrderIndividual(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    percentage = models.IntegerField()

    delivery_begin = models.DateField()
    delivery_end = models.DateField()

    can_deliver = models.BooleanField()

admin.site.register(OrderIndividual)

class OrderCombinedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey('OrderCombined', on_delete=models.CASCADE)
    payment = models.DecimalField(max_digits=4, decimal_places=2)
    
    is_deliverer = models.BooleanField()
    is_complete = models.BooleanField()

class OrderCombined(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, through=OrderCombinedUser)


