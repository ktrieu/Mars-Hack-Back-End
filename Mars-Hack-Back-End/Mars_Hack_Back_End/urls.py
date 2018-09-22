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
]
