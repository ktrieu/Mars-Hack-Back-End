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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

admin.site.register(User)

class Product(models.Model):

    store = models.CharField(max_length=30)
    name = models.CharField(max_length=30)

    price = models.DecimalField(max_digits=5, decimal_places=2)

    description = models.TextField()

    def __str__(self):
        return self.name

admin.site.register(Product)