# website/apis/urls.py

from django.urls import path
from website.apis import views
from rest_framework.authtoken import views as authtoken_views
urlpatterns = [
    
    path('token/',authtoken_views.obtain_auth_token, name='api-token-auth'),
    # API endpoints
    path('products/', views.get_products, name='get-products'),
    path('products/add/', views.add_product, name='add-product'),
    
    # New endpoints for update and delete, using the product's primary key
    path('products/<int:pk>/update/', views.update_product, name='update-product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete-product'),
]