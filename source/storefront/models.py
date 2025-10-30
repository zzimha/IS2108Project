from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Product(models.Model):
    """Product model for the storefront"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=10)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Promotional fields
    is_on_sale = models.BooleanField(default=False)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_current_price(self):
        """Return current price (discounted if on sale). Prioritize consistent derivation from original_price and discount_percentage when available."""
        if self.is_on_sale:
            # If both original and discount% are present, derive sale price
            if self.original_price and self.discount_percentage:
                try:
                    return (self.original_price * (Decimal(100 - int(self.discount_percentage)) / Decimal(100))).quantize(Decimal('0.01'))
                except Exception:
                    return self.price
            # If only original is present, assume stored price is already discounted
            if self.original_price:
                return self.price
            # If only discount% is present, discount the stored price
            if self.discount_percentage:
                try:
                    return (self.price * (Decimal(100 - int(self.discount_percentage)) / Decimal(100))).quantize(Decimal('0.01'))
                except Exception:
                    return self.price
        return self.price
    
    def get_discount_percentage(self):
        """Calculate discount percentage consistently."""
        if not self.is_on_sale:
            return 0
        if self.discount_percentage:
            return int(self.discount_percentage)
        if self.original_price and self.price:
            try:
                discount = ((self.original_price - self.price) / self.original_price) * 100
                return int(round(discount))
            except Exception:
                return 0
        return 0

    class Meta:
        ordering = ['-created_at']


class Customer(models.Model):
    """Customer profile model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('P', 'Prefer not to say'),
    ]
    
    EMPLOYMENT_CHOICES = [
        ('Employed', 'Employed'),
        ('Self-Employed', 'Self-Employed'),
        ('Unemployed', 'Unemployed'),
        ('Student', 'Student'),
    ]
    
    INCOME_CHOICES = [
        ('Below 30k', 'Below 30k'),
        ('30k-60k', '30k-60k'),
        ('60k-100k', '60k-100k'),
        ('Above 100k', 'Above 100k'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='P')
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_CHOICES, default='Employed')
    income_range = models.CharField(max_length=20, choices=INCOME_CHOICES, default='Below 30k')
    preferred_category = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} ({self.user.username})"


class Cart(models.Model):
    """Shopping cart model"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.customer.user.username}"

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        return self.product.get_current_price() * self.quantity


class Order(models.Model):
    """Order model"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.username}"


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        return self.price * self.quantity


class Favorite(models.Model):
    """User favorites for products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    notify_when_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
