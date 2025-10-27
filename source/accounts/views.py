from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from storefront.models import Customer

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validation checks
        errors = []
        
        # Check username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('accounts:register')
        
        # Password validation
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('accounts:register')
        
        if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
            messages.error(request, 'Password must include at least one letter and one number.')
            return redirect('accounts:register')
        
        # Check if password is same as username or email
        if password.lower() == username.lower() or password.lower() == email.lower().split('@')[0]:
            messages.error(request, 'Password cannot be the same as your username or email.')
            return redirect('accounts:register')
        
        # Block common passwords
        common_passwords = ['password123', '12345678', 'password', '123456', 'admin123', 'qwerty123']
        if password.lower() in common_passwords:
            messages.error(request, 'Please choose a stronger password.')
            return redirect('accounts:register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, 'Registration successful!')
        return redirect('accounts:login')
    
    # Clear any old messages when loading the registration page
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'accounts/register.html')

def login_view(request):
    # Clear any old messages when loading the login page
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('storefront:index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def profile(request):
    # Clear any old messages when loading the profile page
    storage = messages.get_messages(request)
    storage.used = True
    
    customer = getattr(request.user, 'customer', None)
    
    # Ensure customer object exists
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            gender='P',
            employment_status='Employed',
            income_range='Below 30k'
        )
    
    return render(request, 'accounts/profile.html', {'customer': customer})

@login_required
def edit_profile(request):
    """Edit profile view"""
    # Clear any old messages when loading the edit profile page (always)
    storage = messages.get_messages(request)
    storage.used = True
    
    customer = getattr(request.user, 'customer', None)
    
    # Ensure customer object exists
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            gender='P',
            employment_status='Employed',
            income_range='Below 30k'
        )
    
    if request.method == 'POST':
        if customer:
            # Update customer profile
            if request.FILES.get('profile_picture'):
                customer.profile_picture = request.FILES.get('profile_picture')
            
            customer.bio = request.POST.get('bio', '')
            
            if request.POST.get('birthday'):
                from datetime import datetime
                try:
                    customer.birthday = datetime.strptime(request.POST.get('birthday'), '%Y-%m-%d').date()
                except:
                    pass
            
            customer.gender = request.POST.get('gender', 'P')
            customer.employment_status = request.POST.get('employment_status', 'Employed')
            customer.income_range = request.POST.get('income_range', 'Below 30k')
            customer.save()
        
        return redirect('accounts:profile')
    
    return render(request, 'accounts/edit_profile.html', {'customer': customer})

def logout_view(request):
    """Logout user"""
    # Clear all existing messages before logging out
    storage = messages.get_messages(request)
    storage.used = True
    
    logout(request)
    # Don't show any message on logout - let the user be redirected cleanly
    return redirect('storefront:index')
