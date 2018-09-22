"""
Definition of models.
"""

from django.db import models

class User(models.Model):
    
    customer_id = models.CharField(max_length=73)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=10)

    income = models.IntegerField()

    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)