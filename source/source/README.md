# AuroraMart - Personalized E-commerce Platform

A B2C e-commerce web application with AI-powered personalized shopping experience built with Django.

## Features

### Storefront
- ✅ User registration and authentication with secure password validation
- ✅ Personalized onboarding with ML-based category recommendation
- ✅ Product browsing by category with images
- ✅ Shopping cart with floating cart icon
- ✅ Checkout with association rules recommendations
- ✅ Order management

### Admin Panel
- ✅ Dashboard with statistics
- ✅ Product and inventory management
- ✅ Customer management
- ✅ Order tracking

### AI/ML Integration
- ✅ Decision Tree Classification for category prediction
- ✅ Association Rules Mining for product recommendations

### Design
- ✅ Modern Poppins typography
- ✅ Responsive 3-column product grid
- ✅ White header with purple branding
- ✅ Clean, professional UI/UX

## Tech Stack

- Django 5.2.6
- SQLite Database
- Python 3.13
- scikit-learn, pandas, joblib for ML models
- Pillow for image handling

## Installation

1. **Navigate to project directory**
   ```bash
   cd source/auroramartproj/auroramart
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Load sample data**
   ```bash
   python manage.py shell < load_initial_data.py
   ```

6. **Start server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Home: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - Register: http://127.0.0.1:8000/accounts/register/

## Project Structure

```
auroramart/
├── accounts/              # User authentication
├── adminpanel/           # Admin management
├── aiengine/             # ML models integration
├── storefront/           # E-commerce frontend
├── auroramart/           # Django settings
├── media/                # Uploaded images
├── ml_models/            # ML model files
├── static/               # Static files (CSS, logos)
└── templates/            # HTML templates
```

## Key URLs

- **Home**: `/`
- **Categories**: `/categories/`
- **Cart**: `/cart/`
- **Profile**: `/accounts/profile/`
- **Admin**: `/admin/`
- **Admin Panel**: `/admin-panel/dashboard/`

## User Flow

1. **Register** → Create account
2. **Login** → Authenticate
3. **Onboarding** → Enter demographics for ML personalization
4. **Browse** → Explore recommended categories
5. **Shop** → Add products to cart
6. **Checkout** → Complete purchase with recommendations
7. **Order** → View order confirmation

## ML Models

- **Decision Tree**: Predicts preferred product category based on user demographics
- **Association Rules**: Recommends complementary products

## Contact

Group 14 - IS2108 Pair Project

