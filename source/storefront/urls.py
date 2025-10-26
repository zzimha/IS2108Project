from django.urls import path
from . import views

app_name = 'storefront'

urlpatterns = [
    path('', views.index, name='index'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<str:category_name>/', views.category_products, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/confirm/', views.confirm_order, name='confirm_order'),
    path('order/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]
