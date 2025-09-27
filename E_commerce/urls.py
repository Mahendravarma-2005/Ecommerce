# E_commerce/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ALL website URLs are included under the root path, allowing Django to find 'login', 'home', etc.
    path('', include('website.urls')), 
]