#!/usr/bin/env python
"""
Diagnostic script to troubleshoot migration issues
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

from django.conf import settings
from django.db import connections
from django.apps import apps
from django.contrib.auth.models import User

print("=" * 70)
print("🔍 MIGRATION DIAGNOSTIC TOOL")
print("=" * 70)

# 1. Check environment
print("\n1️⃣ ENVIRONMENT")
print(f"   DATABASE_URL set: {bool(os.getenv('DATABASE_URL'))}")
if os.getenv('DATABASE_URL'):
    # Hide password
    url = os.getenv('DATABASE_URL')
    if '@' in url:
        parts = url.split('@')
        masked = parts[0].split(':')[:-1]
        masked.append('****')
        print(f"   DATABASE_URL: {':'.join(masked)}@{parts[1]}")

# 2. Check database configuration
print("\n2️⃣ DATABASE CONFIGURATION")
print(f"   Available databases: {list(settings.DATABASES.keys())}")

for db_name, db_config in settings.DATABASES.items():
    print(f"\n   [{db_name}]")
    print(f"   Engine: {db_config['ENGINE']}")
    if 'NAME' in db_config:
        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            db_path = Path(db_config['NAME'])
            print(f"   Path: {db_path}")
            print(f"   Exists: {db_path.exists()}")
            if db_path.exists():
                print(f"   Size: {db_path.stat().st_size:,} bytes")
        else:
            print(f"   Database: {db_config.get('NAME', 'N/A')}")
            print(f"   Host: {db_config.get('HOST', 'N/A')}")
            print(f"   Port: {db_config.get('PORT', 'N/A')}")

# 3. Test connections
print("\n3️⃣ CONNECTION TESTS")
for db_name in settings.DATABASES.keys():
    try:
        conn = connections[db_name]
        conn.ensure_connection()
        print(f"   [{db_name}] ✅ Connected successfully")
    except Exception as e:
        print(f"   [{db_name}] ❌ Connection failed: {str(e)}")

# 4. Count records
print("\n4️⃣ RECORD COUNTS")

# Get User counts
try:
    sqlite_users = User.objects.using('sqlite').count() if 'sqlite' in settings.DATABASES else 0
    pg_users = User.objects.using('default').count()
    print(f"   Users (SQLite): {sqlite_users}")
    print(f"   Users (PostgreSQL): {pg_users}")
except Exception as e:
    print(f"   Error counting users: {e}")

# Get all models
print("\n   Custom App Models:")
for model in apps.get_models():
    if not model._meta.app_label.startswith('django.contrib') and not model._meta.abstract:
        try:
            if 'sqlite' in settings.DATABASES:
                sqlite_count = model.objects.using('sqlite').count()
            else:
                sqlite_count = 0
            pg_count = model.objects.using('default').count()
            
            model_name = f"{model._meta.app_label}.{model.__name__}"
            if sqlite_count > 0 or pg_count > 0:
                print(f"   {model_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
        except Exception as e:
            pass

# 5. Check JSON fixture
print("\n5️⃣ JSON FIXTURE CHECK")
backup_dir = Path(__file__).resolve().parent / 'backups'
if backup_dir.exists():
    json_files = sorted(backup_dir.glob('data_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if json_files:
        latest = json_files[0]
        print(f"   Latest fixture: {latest.name}")
        print(f"   Size: {latest.stat().st_size:,} bytes")
        
        # Try to parse it
        try:
            import json
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   Total records: {len(data)}")
            
            # Count by model
            from collections import Counter
            model_counts = Counter(d['model'] for d in data)
            print(f"   Models in fixture:")
            for model, count in sorted(model_counts.items()):
                print(f"      {model}: {count}")
        except Exception as e:
            print(f"   ⚠️ Error reading fixture: {e}")
    else:
        print("   ⚠️ No data_*.json files found")
else:
    print("   ⚠️ backups/ directory not found")

# 6. Recommendations
print("\n6️⃣ RECOMMENDATIONS")

if 'sqlite' in settings.DATABASES:
    sqlite_users = User.objects.using('sqlite').count()
    pg_users = User.objects.using('default').count()
    
    if sqlite_users > 0 and pg_users == 0:
        print("   ❌ Data exists in SQLite but NOT in PostgreSQL")
        print("   📝 Run these commands:")
        print("      1. python manage.py dump_from_sqlite")
        print("      2. python manage.py loaddata backups\\data_<timestamp>.json")
        print("      3. python manage.py reset_sequences")
    elif sqlite_users > 0 and pg_users > 0 and sqlite_users != pg_users:
        print("   ⚠️ Data counts don't match between databases")
        print("   📝 Run: python manage.py check_counts")
    elif pg_users > 0:
        print("   ✅ Data appears to be in PostgreSQL")
        print("   📝 Verify with: python manage.py check_counts")
    else:
        print("   ⚠️ No data found in either database")
else:
    pg_users = User.objects.using('default').count()
    if pg_users == 0:
        print("   ❌ No data in PostgreSQL")
        print("   ⚠️ SQLite database not configured - migration may not be complete")

print("\n" + "=" * 70)


