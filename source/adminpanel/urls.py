from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_management, name='product_management'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('stock/', views.stock_management, name='stock_management'),
    path('customers/', views.customer_list, name='customers'),
]
