from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from storefront.models import Product

@login_required
def dashboard(request):
    products = Product.objects.all()
    return render(request, 'adminpanel/dashboard.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        category = request.POST['category']
        stock = request.POST['stock']
        Product.objects.create(name=name, price=price, category=category, stock=stock)
        return redirect('adminpanel:admin_dashboard')
    return render(request, 'adminpanel/add_product.html')

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.save()
        return redirect('adminpanel:admin_dashboard')
    return render(request, 'adminpanel/edit_product.html', {'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('adminpanel:admin_dashboard')

@login_required
def stock_management(request):
    low_stock = Product.objects.filter(stock__lte=10)
    return render(request, 'adminpanel/stock.html', {'low_stock': low_stock})
