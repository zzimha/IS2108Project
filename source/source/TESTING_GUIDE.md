# AuroraMart Testing Guide

## 🚀 Quick Start

### Option 1: Using the script
```bash
cd source/auroramartproj/auroramart
./start_server.sh
```

### Option 2: Manual start
```bash
cd source/auroramartproj/auroramart
python3 manage.py migrate
python3 manage.py runserver
```

## 🌐 Access the Application

Once the server is running, open your browser and go to:
- **Home Page**: http://127.0.0.1:8000/
- **Register**: http://127.0.0.1:8000/accounts/register/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **Admin Panel**: http://127.0.0.1:8000/admin-panel/dashboard/

## ✅ Testing Checklist

### 1. **As a New Customer** (Recommended first test)

#### Step 1: Register
1. Go to http://127.0.0.1:8000/accounts/register/
2. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - First Name: `Test`
   - Last Name: `User`
   - Password: `testpass123`
3. Click "Create Account"
4. You should be redirected to login page

#### Step 2: Login
1. Go to http://127.0.0.1:8000/accounts/login/
2. Enter username and password
3. Click "Sign In"
4. You should be redirected to onboarding page

#### Step 3: Complete Onboarding
1. Fill in demographics:
   - Age: `25`
   - Gender: `Male`
   - Employment: `Student`
   - Monthly Income: `2000`
2. Click "Start Shopping"
3. Should redirect to recommended category

#### Step 4: Browse & Shop
1. Browse products on the home page
2. Click on a category to see products
3. Click on a product to see details
4. Click "Add to Cart" (quantity 1)
5. Product should be added to cart

#### Step 5: View Cart
1. Click "Cart" in navigation
2. See your cart items
3. Verify subtotals are correct

#### Step 6: Checkout
1. Click "Proceed to Checkout"
2. Review order summary
3. See recommendations (if any)
4. Click "Confirm Purchase"
5. See order confirmation with order number

### 2. **As an Admin User**

#### Create Admin User (First Time Only)
```bash
python3 manage.py createsuperuser
# Enter username, email, and password
```

#### Test Admin Features
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Navigate through:
   - Products (view, add, edit)
   - Customers (view customer data)
   - Orders (view orders)
   - Carts (view cart data)

#### Test Admin Panel
1. Go to http://127.0.0.1:8000/admin-panel/dashboard/
2. See dashboard statistics:
   - Total products
   - Low stock alert
   - Total customers
   - Total orders
3. Click on Products to manage products
4. Click on Stock to manage inventory

### 3. **Test ML Features**

#### Decision Tree (Onboarding)
1. Register a new user
2. Complete onboarding with different demographics
3. Check if preferred category changes based on input
4. Verify redirection to recommended category

#### Association Rules (Recommendations)
1. Add a product to cart
2. Go to checkout
3. Check for "You might also like" recommendations
4. Verify recommendations are relevant to cart items

## 🔍 Key Features to Test

### ✅ Authentication
- [ ] Register new user
- [ ] Login with credentials
- [ ] Logout
- [ ] View profile
- [ ] Cannot access cart without login

### ✅ Onboarding
- [ ] Complete onboarding form
- [ ] View personalized category recommendation
- [ ] Customer profile saved correctly

### ✅ Product Browsing
- [ ] View featured products on home
- [ ] Browse products by category
- [ ] Click product to see details
- [ ] View product price, description, stock
- [ ] See product ratings

### ✅ Shopping Cart
- [ ] Add product to cart
- [ ] View cart items
- [ ] See correct totals
- [ ] Remove items from cart
- [ ] Update quantities (if implemented)

### ✅ Checkout
- [ ] View checkout page
- [ ] See order summary
- [ ] See recommendations
- [ ] Confirm order
- [ ] Receive order confirmation

### ✅ Order Management
- [ ] Order appears in admin
- [ ] Order status tracked
- [ ] Stock decreases after order
- [ ] Order items saved correctly

### ✅ Admin Panel
- [ ] Access dashboard
- [ ] View statistics
- [ ] Manage products
- [ ] View customers
- [ ] Monitor stock levels

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
python3 manage.py runserver 8001
```

### Database errors
```bash
# Reset database (WARNING: Deletes all data!)
rm db.sqlite3
python3 manage.py migrate
python3 manage.py createsuperuser
```

### Import errors
```bash
# Install dependencies
pip3 install -r requirements.txt
```

### ML models not loading
- Check if `ml_models/` directory exists
- Check if model files are present
- Application will still run without ML (with basic recommendations)

## 📊 Expected Behavior

### Home Page
- Shows featured products
- Has category navigation
- Has login/register links (if not logged in)
- Has cart link (if logged in)

### After Login
- New users → Onboarding
- Existing users → Home page or onboarding (if not completed)

### Cart
- Only accessible when logged in
- Shows all cart items
- Displays total amount
- Has checkout button

### Checkout
- Shows order summary
- Shows recommendations
- Creates order on confirmation
- Updates stock
- Clears cart

## 🎯 Test User Flow Example

**Quick Test Scenario:**
1. Register as "alice"
2. Login
3. Complete onboarding (age: 30, gender: Female, employment: Employed, income: 50000)
4. Browse to recommended category
5. Add 2 products to cart
6. View cart (should see 2 items)
7. Go to checkout
8. Confirm purchase
9. See order confirmation
10. Check admin panel to verify order

---

## 💡 Tips for Testing

1. **Test in Incognito Mode**: Prevents cookie/session conflicts
2. **Create Multiple Users**: Test different demographics
3. **Test Edge Cases**: Empty cart, out of stock items, etc.
4. **Check Stock Updates**: Add to cart, complete order, verify stock decreased
5. **Test Admin**: Create superuser and test admin features

---

**Happy Testing! 🛍️**

