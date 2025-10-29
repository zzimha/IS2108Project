from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('add/', views.add_product, name='admin_add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='admin_edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='admin_delete_product'),
    path('stock/', views.stock_management, name='admin_stock'),
]
