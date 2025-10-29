from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from storefront.models import Product, OrderItem, Order
from .forms import ProductForm
import json


def staff_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(staff_required)
def dashboard(request):
    products = Product.objects.all()

    # Filter orders to include only non-cancelled
    valid_orders = Order.objects.exclude(status='Cancelled')

    # Time-series aggregations (sales revenue)
    def aggregate_sales_by(trunc_fn, queryset, periods):
        qs = (
            OrderItem.objects.filter(order__in=queryset)
            .annotate(period=trunc_fn(F('order__created_at')))
            .values('period')
            .annotate(total=Sum(F('price') * F('quantity')))
            .order_by('period')
        )
        labels = [x['period'].strftime('%Y-%m-%d') if hasattr(x['period'], 'strftime') else str(x['period']) for x in qs]
        data = [float(x['total'] or 0) for x in qs]
        return {'labels': labels[-periods:], 'data': data[-periods:]}

    sales_daily = aggregate_sales_by(TruncDay, valid_orders, periods=30)
    sales_weekly = aggregate_sales_by(TruncWeek, valid_orders, periods=12)
    sales_monthly = aggregate_sales_by(TruncMonth, valid_orders, periods=12)
    sales_yearly = aggregate_sales_by(TruncYear, valid_orders, periods=5)

    sales_timeseries = {
        'daily': sales_daily,
        'weekly': sales_weekly,
        'monthly': sales_monthly,
        'yearly': sales_yearly,
    }

    # Category pie (revenue by product category)
    category_qs = (
        OrderItem.objects.filter(order__in=valid_orders)
        .values('product__category')
        .annotate(total=Sum(F('price') * F('quantity')))
        .order_by('-total')
    )
    category_labels = [row['product__category'] or 'Uncategorized' for row in category_qs]
    category_data = [float(row['total'] or 0) for row in category_qs]

    raw_categories = (
        Product.objects
        .values_list('category', flat=True)
        .exclude(category__isnull=True)
        .exclude(category__exact='')
    )
    # Normalize categories to remove duplicate variants (trim/case)
    categories = sorted({(c or '').strip() for c in raw_categories}, key=lambda x: x.lower())
    
    context = {
        'products': products,
        'categories': categories,
        'sales_timeseries_json': json.dumps(sales_timeseries),
        'category_pie_json': json.dumps({'labels': category_labels, 'data': category_data}),
    }
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
@user_passes_test(staff_required)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('adminpanel:admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'adminpanel/add_product.html', {'form': form})

@login_required
@user_passes_test(staff_required)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('adminpanel:admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'adminpanel/edit_product.html', {'form': form, 'product': product})

@login_required
@user_passes_test(staff_required)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('adminpanel:admin_dashboard')

@login_required
@user_passes_test(staff_required)
def stock_management(request):
    low_stock = Product.objects.filter(stock__lte=10)
    return render(request, 'adminpanel/stock.html', {'low_stock': low_stock})
