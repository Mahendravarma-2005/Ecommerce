# website/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from .models import Product, Cart, CartItem 
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


@login_required(login_url='login') 
def search(request):
    """ Renders the home page with products filtered by a search query. """
    query = request.GET.get("q")
    products = Product.objects.filter(productname__icontains=query) if query else []
    return render(request, 'website/home.html', {"search": query, "products": products})


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
# Cart Views 
# -------------------------

@login_required(login_url='login')
def add_to_cart(request, product_id):
    """ Handles adding a product to the user's cart. """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1 
            
        if quantity <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect('products_list')

        # 1. Get or create the user's Cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # 2. Add or update the CartItem
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # If item already exists, increase quantity
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f"Added {quantity} more {product.productname}(s) to your cart.")
        else:
            messages.success(request, f"{quantity} x {product.productname} added to your cart!")

        return redirect('cart_view') 
    
    return redirect('products_list') 


@login_required(login_url='login')
def cart_view(request):
    """
    Renders the cart page with actual items for the current user.
    """
    try:
        cart = Cart.objects.get(user=request.user)
        # Select CartItems belonging to the user's cart
        cart_items = cart.items.select_related('product') 
    except Cart.DoesNotExist:
        cart_items = None
        
    context = {
        'cart_items': cart_items,
        # Calculate subtotal using list comprehension, safely handling empty cart
        'subtotal': sum(item.get_total_price() for item in (cart_items or []))
    }
    
    return render(request, 'website/cart.html', context)


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    """
    Handles removing a specific CartItem from the user's cart.
    Expects a POST request from the button in cart.html.
    """
    if request.method == 'POST':
        # 1. Get the CartItem or return 404
        # We use item_id here because cart.html passes the CartItem's ID
        cart_item = get_object_or_404(CartItem, id=item_id)

        # 2. Security Check: Ensure the item belongs to the current user's cart
        if cart_item.cart.user != request.user:
            messages.error(request, "Error: You do not have permission to remove that item.")
            return redirect('cart_view')

        # 3. Delete the item
        product_name = cart_item.product.productname 
        cart_item.delete()
        
        messages.success(request, f"**{product_name}** has been removed from your cart.")
        return redirect('cart_view')
    
    # If a user somehow navigates here with a GET request, redirect them
    messages.error(request, "Invalid request method.")
    return redirect('cart_view')