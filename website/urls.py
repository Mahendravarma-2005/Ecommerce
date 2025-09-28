# website/urls.py

from django.urls import path, include
from website import views

urlpatterns = [
    # ... (Existing Core Template Endpoints)
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('search/', views.search, name='search'),

    # NEW: Cart View Path
    path('cart/', views.cart_view, name='cart_view'),
    
    # NEW: Add to Cart Path (for form submission from product list)
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), 
    
    # ⭐ NEW: Remove from Cart Path
    # This URL pattern expects the CartItem's ID (item_id) to identify the item to remove.
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # ... (Existing Product and User Endpoints)
    path('products/list/', views.products_list, name='products_list'),
    path('products/add/', views.add_product_page, name='add_product_page'), 

    path('users/list/', views.user_list, name='user_list'),
    path('users/add/', views.add_user_page, name='add_user_page'), 

    path('apis/', include('website.apis.urls'))
]