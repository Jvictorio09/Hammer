#!/usr/bin/env python
"""
Force clean PostgreSQL - uses raw SQL to drop and recreate all tables
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

from django.core.management import call_command
from django.db import connection

print("=" * 70)
print("🔥 FORCE CLEAN POSTGRESQL")
print("=" * 70)

print("\n⚠️  This will:")
print("   1. Drop ALL tables in PostgreSQL")
print("   2. Re-create them fresh")
print("   3. SQLite will NOT be affected")

response = input("\nContinue? (yes/no): ")
if response.lower() != 'yes':
    print("❌ Aborted.")
    sys.exit(0)

print("\n⏳ Step 1: Getting list of all tables...")

with connection.cursor() as cursor:
    # Get all table names
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"   Found {len(tables)} tables")
    
    if tables:
        print("\n⏳ Step 2: Dropping all tables...")
        
        # Drop all tables
        for table in tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                print(f"   ✓ Dropped {table}")
            except Exception as e:
                print(f"   ⚠️  Error dropping {table}: {e}")

print("\n⏳ Step 3: Re-creating tables with migrations...")
call_command('migrate', verbosity=1)

print("\n✅ PostgreSQL cleaned and reset successfully!")
print("\n📝 Next steps:")
print("   1. python manual_load_data.py")
print("   2. python manage.py reset_sequences")
print("   3. python diagnose_migration.py")

print("\n" + "=" * 70)

