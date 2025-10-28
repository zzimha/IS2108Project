"""
AuroraMart - Complete Setup & Data Loading Script

This script:
1. Loads products from CSV into Django
2. Loads customers from CSV into Django  
3. Generates association rules from transactions (if available)
4. Sets up the database with sample data

Run: python manage.py shell < load_initial_data.py
"""

import pandas as pd
import os
import sys
from decimal import Decimal

# Import Django models
from storefront.models import Product, Customer
from django.contrib.auth.models import User

print("=" * 60)
print("🚀 AuroraMart Initial Data Loading")
print("=" * 60)

# ============================================================
# STEP 1: Load Products from CSV
# ============================================================
print("\n📦 STEP 1: Loading Products...")
print("-" * 60)

try:
    products_df = pd.read_csv('b2c_products_500.csv')
    print(f"✓ Found CSV with {len(products_df)} products")
    
    created_count = 0
    for idx, row in products_df.iterrows():
        try:
            # Map CSV columns to Product model
            product, created = Product.objects.get_or_create(
                name=row['Product name'],
                defaults={
                    'description': row['Product description'],
                    'category': row['Product Category'],
                    'price': Decimal(str(row['Unit price'])),
                    'stock': int(row['Quantity on hand']),
                    'reorder_threshold': int(row['Reorder Quantity']),
                    'rating': Decimal(str(row['Product rating'])) if pd.notna(row['Product rating']) else None,
                }
            )
            if created:
                created_count += 1
                
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"  Progress: {idx + 1}/{len(products_df)} products processed")
                
        except Exception as e:
            print(f"  ⚠ Error loading product {idx}: {e}")
            continue
    
    print(f"✓ Successfully loaded {created_count} products into database")
    
except FileNotFoundError:
    print("✗ ERROR: b2c_products_500.csv not found!")
    print("  Place the CSV file in the auroramartproj directory")
except Exception as e:
    print(f"✗ ERROR loading products: {e}")

# ============================================================
# STEP 2: Load Customers from CSV
# ============================================================
print("\n👥 STEP 2: Loading Customers...")
print("-" * 60)

try:
    customers_df = pd.read_csv('b2c_customers_100.csv')
    print(f"✓ Found CSV with {len(customers_df)} customers")
    
    created_count = 0
    for idx, row in customers_df.iterrows():
        try:
            # Create Django User first
            username = f"customer_{idx + 1}"
            email = f"customer{idx + 1}@auroramart.com"
            
            # Create or get user
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Customer {idx + 1}',
                }
            )
            
            # Create or update Customer profile
            customer, cust_created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'age': int(row['age']) if pd.notna(row['age']) else None,
                    'gender': 'M' if row['gender'] == 'Male' else 'F' if row['gender'] == 'Female' else 'O',
                    'employment_status': row['employment_status'] if pd.notna(row['employment_status']) else 'Employed',
                    'income_range': 'Below 30k',  # You might want to derive this from monthly_income_sgd
                    'preferred_category': row['preferred_category'] if pd.notna(row['preferred_category']) else None,
                }
            )
            
            if cust_created:
                created_count += 1
                
            if (idx + 1) % 20 == 0:
                print(f"  Progress: {idx + 1}/{len(customers_df)} customers processed")
                
        except Exception as e:
            print(f"  ⚠ Error loading customer {idx}: {e}")
            continue
    
    print(f"✓ Successfully loaded {created_count} customers into database")
    
except FileNotFoundError:
    print("✗ ERROR: b2c_customers_100.csv not found!")
except Exception as e:
    print(f"✗ ERROR loading customers: {e}")

# ============================================================
# STEP 3: Generate Association Rules (if transactions CSV exists)
# ============================================================
print("\n🔗 STEP 3: Generating Association Rules...")
print("-" * 60)

try:
    # Check if transactions file exists
    if os.path.exists('b2c_products_500_transactions_50k.csv'):
        print("✓ Found transactions CSV, generating association rules...")
        
        import joblib
        from mlxtend.frequent_patterns import apriori, association_rules
        
        # Load transaction data
        trans_df = pd.read_csv('b2c_products_500_transactions_50k.csv')
        print(f"  Loaded {len(trans_df)} transactions")
        
        # Run Apriori algorithm
        print("  Running Apriori algorithm...")
        frequent_itemsets = apriori(trans_df, min_support=0.1, use_colnames=True)
        print(f"  Found {len(frequent_itemsets)} frequent itemsets")
        
        # Generate association rules
        print("  Generating association rules...")
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
        print(f"  Generated {len(rules)} association rules")
        
        # Save rules
        joblib.dump(rules, 'ml_models/association_rules_model.joblib')
        print("✓ Saved association rules to ml_models/association_rules_model.joblib")
        
    else:
        print("⚠ Transactions CSV not found (b2c_products_500_transactions_50k.csv)")
        print("  You can skip this for now - will use dummy recommendations")
        
        # Create dummy rules for testing
        import joblib
        dummy_rules = []
        joblib.dump(dummy_rules, 'ml_models/association_rules_model.joblib')
        print("  Created empty association rules file for testing")
        
except ImportError:
    print("⚠ mlxtend not installed - skipping association rules generation")
    print("  Run: pip install mlxtend")
except Exception as e:
    print(f"⚠ WARNING: Could not generate association rules: {e}")

# ============================================================
# STEP 4: Summary
# ============================================================
print("\n" + "=" * 60)
print("✓ DATA LOADING COMPLETE!")
print("=" * 60)

print("\n📊 Database Summary:")
print(f"  Products in database: {Product.objects.count()}")
print(f"  Customers in database: {Customer.objects.count()}")
print(f"  Users in database: {User.objects.count()}")

print("\n📁 ML Models:")
if os.path.exists('ml_models/decision_tree_model.joblib'):
    print("  ✓ Decision Tree model ready")
else:
    print("  ✗ Decision Tree model NOT found")

if os.path.exists('ml_models/association_rules_model.joblib'):
    print("  ✓ Association Rules model ready")
else:
    print("  ✗ Association Rules model NOT found")

print("\n🚀 Next Steps:")
print("  1. Run: python manage.py runserver")
print("  2. Visit: http://127.0.0.1:8000/")
print("  3. Go to admin: http://127.0.0.1:8000/admin/")
print("  4. Login with your superuser account")
print("  5. Test the storefront!")

print("\n" + "=" * 60)
