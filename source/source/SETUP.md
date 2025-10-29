# AuroraMart Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd source/auroramartproj/auroramart
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
# Enter username, email, password when prompted
```

### 3. Load Sample Data
```bash
# This will load products and customers from CSV files
python manage.py shell < load_initial_data.py
```

### 4. Start the Server
```bash
python manage.py runserver
```

### 5. Access the Application
- **Home**: http://127.0.0.1:8000/
- **Register**: http://127.0.0.1:8000/accounts/register/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **Admin Panel**: http://127.0.0.1:8000/admin-panel/dashboard/

## Test the Application

### As a Customer:
1. Register a new account at `/accounts/register/`
2. Login at `/accounts/login/`
3. Complete onboarding (enter demographics)
4. Browse recommended products
5. Add products to cart
6. Checkout and complete order

### As an Admin:
1. Login with superuser credentials at `/admin/`
2. Or access admin panel at `/admin-panel/dashboard/`
3. View dashboard statistics
4. Manage products
5. Monitor stock levels
6. View customers

## Important Notes

- Make sure the `b2c_products_500.csv` and `b2c_customers_100.csv` files are in the `auroramart` directory
- The ML models (`decision_tree_model.joblib`, `association_rules_model.joblib`) should be in the `ml_models/` directory
- If models are missing, the application will still run but without ML recommendations

## Troubleshooting

### Port already in use
```bash
python manage.py runserver 8001  # Use different port
```

### Database errors
```bash
# Reset database (WARNING: Deletes all data!)
rm db.sqlite3
python manage.py migrate
python manage.py shell < load_initial_data.py
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

