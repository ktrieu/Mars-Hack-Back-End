"""
Definition of urls for Mars_Hack_Back_End.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', app.views.home),
    url(r'^admin/', admin.site.urls),
]
