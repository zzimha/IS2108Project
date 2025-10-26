from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Customer, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
import joblib
import os
from django.conf import settings

# Load ML models
decision_tree_model = None
association_rules = None

try:
    dt_path = os.path.join(settings.BASE_DIR, 'ml_models', 'decision_tree_model.joblib')
    ar_path = os.path.join(settings.BASE_DIR, 'ml_models', 'association_rules_model.joblib')
    if os.path.exists(dt_path):
        decision_tree_model = joblib.load(dt_path)
    if os.path.exists(ar_path):
        association_rules = joblib.load(ar_path)
except Exception as e:
    print(f"Warning: Could not load ML models: {e}")

def index(request):
    """Home page showing featured products"""
    # Use the 6 specific products that have images uploaded
    # Product IDs: 189, 74, 110, 148, 111, 134
    featured_product_ids = [189, 74, 110, 148, 111, 134]
    featured_products = Product.objects.filter(id__in=featured_product_ids, stock__gt=0)
    
    # Show only 3 categories on home page
    categories = ['Beauty & Personal Care', 'Home & Kitchen', 'Fashion']
    
    # Get cart count if user is logged in
    cart_count = 0
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            cart = Cart.objects.get(customer=customer)
            cart_count = cart.items.count()
        except:
            cart_count = 0
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'cart_count': cart_count,
    }
    return render(request, 'storefront/index.html', context)

def get_or_create_customer(user):
    """Helper to get or create customer profile"""
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return Customer.objects.create(user=user)

def get_or_create_cart(customer):
    """Helper to get or create shopping cart"""
    cart, created = Cart.objects.get_or_create(customer=customer)
    return cart

@login_required
def onboarding(request):
    """Onboarding page for new users - collects demographics and predicts preferred category"""
    if request.method == 'POST':
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        employment = request.POST.get('employment')
        income = request.POST.get('income')
        
        # Save customer profile
        customer = get_or_create_customer(request.user)
        customer.age = int(age)
        customer.gender = 'M' if gender == 'male' else 'F' if gender == 'female' else 'P'
        customer.employment_status = employment
        
        # Map income range
        income_val = int(income)
        if income_val < 30000:
            customer.income_range = 'Below 30k'
        elif income_val < 60000:
            customer.income_range = '30k-60k'
        elif income_val < 100000:
            customer.income_range = '60k-100k'
        else:
            customer.income_range = 'Above 100k'
        customer.save()
        
        # Predict preferred category using decision tree
        preferred_category = None
        if decision_tree_model is not None:
            try:
                # Prepare features for decision tree
                features = [[
                    int(age),
                    1 if gender == 'male' else 0,
                    # Add more feature encoding as needed
                ]]
                pred_category = decision_tree_model.predict(features)[0]
                customer.preferred_category = pred_category
                customer.save()
                preferred_category = pred_category
            except Exception as e:
                print(f"Error predicting category: {e}")
        
        # Create cart for customer
        get_or_create_cart(customer)
        
        messages.success(request, f'Welcome to AuroraMart! We recommend browsing {preferred_category or "our products"} for you.')
        
        # Redirect to preferred category or index
        if preferred_category:
            return redirect('storefront:category_products', category_name=preferred_category)
        return redirect('storefront:index')
    
    return render(request, 'storefront/onboarding.html')

def category_list(request):
    """List all product categories"""
    # Show 10 specific categories
    categories = [
        'Beauty & Personal Care',
        'Home & Kitchen',
        'Fashion',
        'Health & Wellness',
        'Sports & Outdoors',
        'Electronics',
        'Pet Supplies',
        'Books',
        'Automotive',
        'Toys & Games',
    ]
    context = {'categories': categories}
    return render(request, 'storefront/category_list.html', context)

def category_products(request, category_name):
    """Show products in a specific category"""
    # Fix category name matching - try both exact and contains
    products = Product.objects.filter(
        category__icontains=category_name,
        stock__gt=0
    )
    
    # Get association rule recommendations
    recommendations = []
    if association_rules is not None and hasattr(association_rules, 'columns'):
        try:
            # Get top 3 recommendations for this category
            recommendations = Product.objects.filter(
                category__icontains=category_name,
                stock__gt=0
            ).order_by('-rating')[:3]
        except:
            pass
    
    context = {
        'category': category_name,
        'products': products,
        'recommendations': recommendations,
    }
    return render(request, 'storefront/category_products.html', context)

def product_detail(request, product_id):
    """Show detailed view of a product"""
    product = get_object_or_404(Product, id=product_id)
    
    # Get "frequently bought together" recommendations using association rules
    recommendations = []
    if association_rules is not None:
        try:
            # Find products in same category or get top rated products
            recommendations = Product.objects.filter(
                category=product.category
            ).exclude(id=product.id).filter(stock__gt=0)[:4]
        except:
            pass
    
    # Get cart count if user is logged in
    cart_count = 0
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            cart = Cart.objects.get(customer=customer)
            cart_count = cart.items.count()
        except:
            cart_count = 0
    
    context = {
        'product': product,
        'recommendations': recommendations,
        'cart_count': cart_count,
    }
    return render(request, 'storefront/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        customer = get_or_create_customer(request.user)
        cart = get_or_create_cart(customer)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
        return redirect('storefront:product_detail', product_id=product_id)
    
    return redirect('storefront:index')

@login_required
def cart(request):
    """View shopping cart"""
    customer = get_or_create_customer(request.user)
    cart = get_or_create_cart(customer)
    cart_items = cart.items.all()
    
    total = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'storefront/cart.html', context)

@login_required
def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.info(request, 'Item removed from cart!')
    
    return redirect('storefront:cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.info(request, 'Item removed from cart!')
    return redirect('storefront:cart')

@login_required
def checkout(request):
    """Checkout page with recommendations based on association rules"""
    customer = get_or_create_customer(request.user)
    cart = get_or_create_cart(customer)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('storefront:cart')
    
    total = sum(item.get_total() for item in cart_items)
    
    # Get recommendations based on association rules
    recommendations = []
    if association_rules is not None:
        try:
            # Get categories of products in cart
            cart_categories = set(item.product.category for item in cart_items)
            
            # Find products in similar or complementary categories
            recommendations = Product.objects.filter(
                category__in=cart_categories
            ).exclude(
                id__in=[item.product.id for item in cart_items]
            ).filter(stock__gt=0).order_by('-rating')[:5]
        except Exception as e:
            print(f"Error getting recommendations: {e}")
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'recommendations': recommendations,
    }
    return render(request, 'storefront/checkout.html', context)

@login_required
def confirm_order(request):
    """Process order confirmation"""
    if request.method == 'POST':
        customer = get_or_create_customer(request.user)
        cart = get_or_create_cart(customer)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.warning(request, 'Your cart is empty!')
            return redirect('storefront:cart')
        
        # Calculate total
        total = sum(item.get_total() for item in cart_items)
        
        # Check stock availability
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(request, f'Insufficient stock for {item.product.name}')
                return redirect('storefront:cart')
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            status='Pending',
            total_amount=total
        )
        
        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Update stock
            item.product.stock -= item.quantity
            item.product.save()
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Order #{order.id} confirmed! Thank you for shopping!')
        return redirect('storefront:order_confirmation', order_id=order.id)
    
    return redirect('storefront:checkout')

def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'storefront/order_confirmation.html', context)

