# website/views.py

from django.shortcuts import render, redirect, get_object_or_404 # IMPORTANT: get_object_or_404 is now imported
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from .models import Product, Cart, CartItem # UPDATED: Cart and CartItem imported
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer, UserRegistrationSerializer


# -------------------------
# Template Views (Django HTML)
# -------------------------

@login_required(login_url='login') 
def home(request):
    """ Renders the protected home page. """
    products = Product.objects.all()
    return render(request, 'website/home.html', {"products": products})

def login(request):
    # If the user is already authenticated, redirect them home immediately
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password) 
        if user is not None:
            auth_login(request, user)
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            
    next_url = request.GET.get('next')
    return render(request, "website/login.html", {'next': next_url})


def logout_view(request):
    """ Logs out the user and redirects to the login page. """
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('login') 

# website/views.py (Search function update)

# ... (imports)

@login_required(login_url='login') # ADD THIS DECORATOR
def search(request):
    """ Renders the home page with products filtered by a search query. """
    query = request.GET.get("q")
    products = Product.objects.filter(productname__icontains=query) if query else []
    return render(request, 'website/home.html', {"search": query, "products": products})
# ...


# -------------------------
# Product Management Views (Protected)
# -------------------------

@login_required(login_url='login')
def products_list(request):
    """ Renders the product list page with actual products for the table. """
    products = Product.objects.all()
    # Passing products to the template so the loop works
    return render(request, 'website/products/products_list.html', {'products': products})

@login_required(login_url='login')
def add_product_page(request):
    """ Renders the add product form and handles the form submission. """
    if request.method == 'POST':
        data = {
            'productname': request.POST.get('productName'), 
            'price': request.POST.get('price'),
            'description': request.POST.get('description')
        }
        serializer = ProductSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            messages.success(request, f"Product '{data['productname']}' added successfully!")
            return redirect('products_list')
        else:
            error_messages = ", ".join([f"{k}: {v[0]}" for k, v in serializer.errors.items()])
            messages.error(request, f"Failed to add product: {error_messages}")
            return render(request, 'website/products/add_products.html', {'form_data': data})
            
    return render(request, 'website/products/add_products.html')

@login_required(login_url='login')
def user_list(request):
    return render(request, 'website/users/user_list.html')

@login_required(login_url='login')
def add_user_page(request):
    return render(request, 'website/users/add_user.html')


# -------------------------
# Cart Views (Functional logic now depends on the models above)
# -------------------------
# website/views.py (Partial)

# ... (rest of imports and views)

@login_required(login_url='login')
def add_to_cart(request, product_id):
    """ Handles adding a product to the user's cart (via POST from product list). """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # NEW: Get quantity from the POST data (defaults to 1 if not provided)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1 # Fallback to 1 if input is non-numeric
            
        if quantity <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect('products_list')

        # 1. Get or create the user's Cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # 2. Add or update the CartItem
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity} # Use the user-provided quantity
        )
        
        if not item_created:
            # If item already exists, increase quantity
            cart_item.quantity += quantity # Add the new quantity to the existing quantity
            cart_item.save()
            messages.success(request, f"Added {quantity} more {product.productname}(s) to your cart.")
        else:
            messages.success(request, f"{quantity} x {product.productname} added to your cart!")

        # Redirect to the cart view to confirm addition
        return redirect('cart_view') # Changed redirect to 'cart_view'
    
    return redirect('products_list') 


@login_required(login_url='login')
def cart_view(request):
    """
    Renders the cart page with actual items for the current user.
    """
    # ... (code remains the same, it correctly uses dynamic context variables)
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product') 
    except Cart.DoesNotExist:
        cart_items = None
        
    context = {
        'cart_items': cart_items,
        'subtotal': sum(item.get_total_price() for item in (cart_items or []))
    }
    
    return render(request, 'website/cart.html', context)