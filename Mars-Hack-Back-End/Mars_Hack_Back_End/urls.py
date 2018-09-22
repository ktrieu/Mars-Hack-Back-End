"""
Definition of urls for Mars_Hack_Back_End.
"""

from datetime import datetime
from django.urls import path
import django.contrib.auth.views

import app.forms
import app.views

from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path(r'', app.views.home),
    path(r'admin', admin.site.urls),
    path(r'api/load_user/<cust_id>', app.views.load_user_from_api),
    path(r'api/get_products', app.views.get_products)
]
