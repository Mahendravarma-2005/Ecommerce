from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Product(models.Model):
    productname = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()

    def __str__(self):
        return self.productname
    

# --- NEW CART MODELS ---

class Cart(models.Model):
    """Represents a shopping cart, tied to a user."""
    # Links cart to the custom AuthUser model (one-to-one)
    user = models.OneToOneField('website.AuthUser', on_delete=models.CASCADE, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
class CartItem(models.Model):
    """Represents a single product instance within a cart, with quantity."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        # Ensures a user can only have one of a particular product in the cart
        unique_together = ('cart', 'product') 

    def get_total_price(self):
        # Helper method for total price of this item
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.productname}"

# --- END NEW CART MODELS ---


#signal to create auth token when a new user is created
@receiver(post_save, sender='website.AuthUser')
def create_auth_user_token(sender, instance, created, **kwargs):
    if created:
        from rest_framework.authtoken.models import Token
        Token.objects.create(user=instance)


class AuthUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    REQUIRED_FIELDS = ['email']
    first_name = None
    last_name = None

    def __str__(self):
        # Corrected: used __str__ instead of _str_
        return self.email