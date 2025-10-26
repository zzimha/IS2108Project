from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, F
from storefront.models import Product, Customer, Order
from django.contrib.auth.models import User

def is_admin(user):
    """Check if user is admin (staff or superuser)"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard showing overview"""
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=F('reorder_threshold')).count()
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def product_management(request):
    """Manage products list"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category=category_filter)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'adminpanel/product_form.html', context)

@login_required
@user_passes_test(is_admin)
def product_edit(request, product_id):
    """Edit a product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.stock = int(request.POST.get('stock', 0))
        product.reorder_threshold = int(request.POST.get('reorder_threshold', 10))
        if request.POST.get('rating'):
            product.rating = request.POST.get('rating')
        product.save()
        
        messages.success(request, f'{product.name} updated successfully!')
        return redirect('adminpanel:product_management')
    
    context = {'product': product}
    return render(request, 'adminpanel/product_form.html', context)

@login_required
@user_passes_test(is_admin)
def stock_management(request):
    """Manage stock levels"""
    # Get products with low stock
    products = Product.objects.filter(stock__lte=F('reorder_threshold')).order_by('stock')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock = int(request.POST.get('new_stock', 0))
        
        product = get_object_or_404(Product, id=product_id)
        product.stock = new_stock
        product.save()
        
        messages.success(request, f'Stock updated for {product.name}!')
        return redirect('adminpanel:stock_management')
    
    context = {'products': products}
    return render(request, 'adminpanel/stock_management.html', context)

@login_required
@user_passes_test(is_admin)
def customer_list(request):
    """List all customers"""
    search_query = request.GET.get('search', '')
    
    customers = Customer.objects.select_related('user').all()
    
    if search_query:
        customers = customers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'adminpanel/customers.html', context)
