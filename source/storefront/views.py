from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Product, Customer, Cart, CartItem, Order, OrderItem, Favorite
from django.contrib.auth.models import User
from decimal import Decimal
import joblib
import os
import json
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
    """Home page showing featured products - personalized based on user profile"""
    # Clear any old messages when loading the homepage
    storage = messages.get_messages(request)
    storage.used = True
    
    # Default featured products (Product IDs: 189, 74, 110, 148, 111, 134)
    default_featured_product_ids = [189, 74, 110, 148, 111, 134]
    
    featured_products = None
    is_personalized = False
    
    # If user is logged in and has profile, show personalized products
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            
            # Check if customer has required profile data (age and gender)
            if customer.age and customer.gender and customer.gender != 'P':
                # Map income range to numeric value
                income_map = {
                    'Below 30k': 1,
                    '30k-60k': 2,
                    '60k-100k': 3,
                    'Above 100k': 3,
                }
                income_level = income_map.get(customer.income_range, 2)
                
                # Map gender to numeric (0 = Male, 1 = Female)
                gender_numeric = 1 if customer.gender == 'F' else 0
                
                # Predict category using Decision Tree model
                predicted_category = None
                if decision_tree_model is not None:
                    try:
                        features = [[customer.age, gender_numeric, income_level]]
                        predicted_category = decision_tree_model.predict(features)[0]
                    except Exception as e:
                        print(f"Error predicting category: {e}")
                
                # If prediction successful, get products from that category
                if predicted_category:
                    # Get products from predicted category (only with images)
                    featured_products = Product.objects.filter(
                        category__icontains=predicted_category,
                        stock__gt=0
                    ).exclude(image='').order_by('-rating')[:6]
                    
                    if featured_products:
                        is_personalized = True
        except Customer.DoesNotExist:
            pass
    
    # Fall back to default featured products if no personalized products
    if not featured_products:
        featured_products = Product.objects.filter(id__in=default_featured_product_ids, stock__gt=0)
    
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
        'is_personalized': is_personalized,
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
    # Clear any old messages when loading the category list page
    storage = messages.get_messages(request)
    storage.used = True
    
    # Show 10 specific categories with product counts
    category_names = [
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
    
    categories = []
    for cat_name in category_names:
        count = Product.objects.filter(category__icontains=cat_name).count()
        categories.append({
            'name': cat_name,
            'count': count,
        })
    
    context = {'categories': categories}
    return render(request, 'storefront/category_list.html', context)

def category_products(request, category_name):
    """Show products in a specific category"""
    # Clear any old messages when loading the category products page
    storage = messages.get_messages(request)
    storage.used = True
    
    # Featured product IDs to prioritize
    featured_product_ids = [189, 74, 110, 148, 111, 134]
    
    # Set max products per category (between 4-9)
    # Specific category limits
    category_limits = {
        'Sports & Outdoors': 4,
        'Pet Supplies': 5,
        'Automotive': 6,
        'Electronics': 6,
        'Health & Wellness': 7,
        'Toys & Games': 4,
        'Books': 5,
    }
    
    # Check which limit applies to this category
    max_products = 9  # default
    for cat_name, limit in category_limits.items():
        if cat_name in category_name:
            max_products = limit
            break
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'recommended')  # default to recommended
    
    # Base query for all products in category (only with images)
    products_query = Product.objects.filter(
        category__icontains=category_name,
        stock__gt=0
    ).exclude(image='')
    
    # Apply search filter if provided
    if search_query:
        products_query = products_query.filter(name__icontains=search_query)
    
    # Only prioritize featured products when sort_by is 'recommended'
    if sort_by == 'recommended':
        # Get featured products that match this category
        featured_in_category = products_query.filter(id__in=featured_product_ids)
        
        # Get other products in this category (excluding already shown featured ones)
        other_products = products_query.exclude(id__in=featured_product_ids)
        
        # Sort other products by rating
        other_products = other_products.order_by('-rating')
        
        # Combine: featured products first, then fill up to max_products
        products_list = list(featured_in_category)
        remaining_slots = max_products - len(products_list)
        
        if remaining_slots > 0:
            additional_products = list(other_products[:remaining_slots])
            products_list.extend(additional_products)
        
        products = products_list[:max_products]
    else:
        # For other sorts, apply sorting to all products (no featured prioritization)
        if sort_by == 'newest':
            products_query = products_query.order_by('-created_at')
        elif sort_by == 'price_high':
            products_query = products_query.order_by('-price')
        elif sort_by == 'price_low':
            products_query = products_query.order_by('price')
        elif sort_by == 'name':
            products_query = products_query.order_by('name')
        else:
            products_query = products_query.order_by('-rating')
        
        # Get products and convert to list
        products = list(products_query)
        # Limit to max_products
        products = products[:max_products]
    
    # Get association rule recommendations
    recommendations = []
    try:
        # Get top 3 recommendations for this category (only with images)
        recommendations = list(Product.objects.filter(
            category__icontains=category_name,
            stock__gt=0
        ).exclude(id__in=[p.id for p in products]).exclude(image='').order_by('-rating'))[:3]
    except:
        pass
    
    context = {
        'category': category_name,
        'products': products,
        'recommendations': recommendations,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'storefront/category_products.html', context)

def product_detail(request, product_id):
    """Show detailed view of a product"""
    # Clear any old messages when loading the product detail page
    storage = messages.get_messages(request)
    storage.used = True
    
    product = get_object_or_404(Product, id=product_id)
    
    # Get "frequently bought together" recommendations using association rules
    recommendations = []
    try:
        # Find products in same category or get top rated products (only with images)
        recommendations = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id).filter(stock__gt=0).exclude(image='')[:3]
    except:
        pass
    
    # Get cart count if user is logged in
    cart_count = 0
    is_favorite = False
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            cart = Cart.objects.get(customer=customer)
            cart_count = cart.items.count()
        except:
            cart_count = 0
        
        # Check if product is favorited
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'recommendations': recommendations,
        'cart_count': cart_count,
        'is_favorite': is_favorite,
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
    # Clear any old messages when loading the cart page
    storage = messages.get_messages(request)
    storage.used = True
    
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
    
    subtotal = sum(item.get_total() for item in cart_items)
    
    # Calculate delivery fee
    delivery_fee = Decimal('4.99')
    free_delivery_threshold = Decimal('150.00')
    
    if subtotal >= free_delivery_threshold:
        delivery_fee = Decimal('0.00')
    
    total = subtotal + delivery_fee
    
    # Get recommendations based on association rules - limit to 3 (only with images)
    recommendations = []
    try:
        # Get categories of products in cart
        cart_categories = set(item.product.category for item in cart_items)
        
        # Find products in similar or complementary categories (only with images)
        recommendations = Product.objects.filter(
            category__in=cart_categories
        ).exclude(
            id__in=[item.product.id for item in cart_items]
        ).filter(stock__gt=0).exclude(image='').order_by('-rating')[:3]
    except Exception as e:
        print(f"Error getting recommendations: {e}")
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'free_delivery_threshold': free_delivery_threshold,
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
        
        # Calculate subtotal and delivery fee
        subtotal = sum(item.get_total() for item in cart_items)
        
        # Calculate delivery fee
        delivery_fee = Decimal('4.99')
        free_delivery_threshold = Decimal('150.00')
        
        if subtotal >= free_delivery_threshold:
            delivery_fee = Decimal('0.00')
        
        total = subtotal + delivery_fee
        
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


@login_required
def toggle_favorite(request, product_id):
    """Toggle favorite status for a product"""
    product = get_object_or_404(Product, id=product_id)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
        messages.info(request, f'{product.name} removed from favorites')
    else:
        is_favorite = True
        messages.success(request, f'{product.name} added to favorites!')
    
    return JsonResponse({'is_favorite': is_favorite})


@login_required
def favorites(request):
    """Display user's favorite products"""
    # Clear any old messages when loading the favorites page
    storage = messages.get_messages(request)
    storage.used = True
    
    favorite_products = Product.objects.filter(
        favorited_by__user=request.user
    ).distinct()
    
    # Get cart count
    cart_count = 0
    try:
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        cart_count = cart.items.count()
    except:
        cart_count = 0
    
    context = {
        'favorite_products': favorite_products,
        'cart_count': cart_count,
    }
    return render(request, 'storefront/favorites.html', context)

@csrf_exempt
def aurabot_reply(request):
    """Handle chatbot replies"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "")
            
            # Simple rule-based responses (no OpenAI for now to avoid API keys)
            responses = {
                "hello": "Hello! I'm AuroBot, your friendly assistant at AuroraMart! How can I help you today?",
                "hi": "Hi there! Welcome to AuroraMart! What can I help you with?",
                "products": "We have a wide range of products! Check out our categories: Beauty & Personal Care, Home & Kitchen, Fashion, Electronics, and more!",
                "order": "To place an order, simply add items to your cart and proceed to checkout. We offer free delivery on orders over $150!",
                "shipping": "We offer fast shipping! Standard delivery is $4.99, and it's FREE for orders over $150!",
                "help": "I can help you with product information, orders, shipping, promotions, and more. Just ask me anything!",
                "price": "Great news! We have many products on sale right now with fantastic discounts. Check out our featured products!",
                "no that's all": "Hope AuroBot could help! Shop Bright and happy shopping! 🌟",
            }
            
            user_lower = user_input.lower()
            reply = f"I understand you're asking about '{user_input}'. At AuroraMart, we're here to help! Visit our product pages for detailed information, or contact our support team for specific inquiries. Is there anything else I can help you with?"
            
            # Check for keywords (check "no thanks" responses first)
            if "no" in user_lower and ("thanks" in user_lower or "thank" in user_lower):
                reply = "Hope AuroBot could help! Shop Bright and happy shopping! 🌟"
            else:
                # Check for other keywords
                for key, response in responses.items():
                    if key in user_lower:
                        reply = response
                        break
            
            return JsonResponse({"reply": reply})
        except Exception as e:
            return JsonResponse({"reply": "I'm having trouble understanding that. Could you please rephrase?"})
    
    return JsonResponse({"reply": "Please send a POST request with a message."})

