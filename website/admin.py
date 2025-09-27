# website/admin.py (UPDATED)

from django.contrib import admin
from .models import Product, AuthUser, Cart, CartItem

# Use Admin classes for better display
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'productname', 'price')
    search_fields = ('productname',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total_price')
    list_filter = ('cart', 'product')

    # Custom method to display total price
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price ($)'

# You can keep the default AuthUser registration simple:
admin.site.register(AuthUser)
# OR if you prefer custom user display, use:
# from django.contrib.auth.admin import UserAdmin
# admin.site.register(AuthUser, UserAdmin)