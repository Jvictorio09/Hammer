#!/usr/bin/env python
"""
Clean PostgreSQL database completely - drops all data from custom tables
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')

from dotenv import load_dotenv
load_dotenv()

django.setup()

from django.db import connection
from django.apps import apps

print("=" * 70)
print("🧹 POSTGRESQL DATABASE CLEANER")
print("=" * 70)

print("\n⚠️  WARNING: This will delete ALL data from PostgreSQL!")
print("   SQLite database will NOT be affected.")

response = input("\nAre you sure you want to continue? (yes/no): ")
if response.lower() != 'yes':
    print("❌ Aborted.")
    sys.exit(0)

print("\n⏳ Cleaning PostgreSQL database...")

# Get all models
all_models = apps.get_models()

# Disable foreign key checks temporarily
with connection.cursor() as cursor:
    # For PostgreSQL, we need to delete in reverse order or disable triggers
    print("\n   Disabling triggers...")
    
    deleted_counts = {}
    
    # Delete data from custom app tables
    for model in reversed(all_models):
        if model._meta.app_label in ['myApp']:  # Only custom apps
            table_name = model._meta.db_table
            try:
                cursor.execute(f'DELETE FROM "{table_name}" CASCADE')
                deleted = cursor.rowcount
                if deleted > 0:
                    deleted_counts[table_name] = deleted
                    print(f"   ✓ Deleted {deleted} records from {table_name}")
            except Exception as e:
                print(f"   ⚠️  Error deleting from {table_name}: {e}")
    
    # Also clear auth users and related tables
    try:
        cursor.execute('DELETE FROM "auth_user" CASCADE')
        deleted = cursor.rowcount
        if deleted > 0:
            deleted_counts['auth_user'] = deleted
            print(f"   ✓ Deleted {deleted} records from auth_user")
    except Exception as e:
        print(f"   ⚠️  Error deleting from auth_user: {e}")
    
    # Reset sequences for all tables
    print("\n   Resetting sequences...")
    for model in all_models:
        if hasattr(model, '_meta') and not model._meta.abstract:
            table_name = model._meta.db_table
            pk_field = model._meta.pk
            if pk_field and pk_field.get_internal_type() in ('AutoField', 'BigAutoField'):
                sequence_name = f'{table_name}_{pk_field.column}_seq'
                try:
                    cursor.execute(f"SELECT setval('{sequence_name}', 1, false)")
                except Exception:
                    pass  # Sequence might not exist

print("\n✅ PostgreSQL database cleaned successfully!")
print(f"\n📊 Summary:")
print(f"   Total tables cleaned: {len(deleted_counts)}")
print(f"   Total records deleted: {sum(deleted_counts.values())}")

print("\n📝 Next steps:")
print("   1. python manage.py migrate")
print("   2. python manual_load_data.py")
print("   3. python manage.py reset_sequences")
print("   4. python diagnose_migration.py")

print("\n" + "=" * 70)

