#!/usr/bin/env python
"""
Manual data loader - troubleshoots and loads JSON fixture into PostgreSQL
"""

import os
import sys
import json
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')

from dotenv import load_dotenv
load_dotenv()

django.setup()

from django.core.management import call_command
from django.core import serializers
from django.db import transaction

print("=" * 70)
print("📦 MANUAL DATA LOADER")
print("=" * 70)

# Find the latest JSON file
backup_dir = Path(__file__).resolve().parent / 'backups'
json_files = sorted(backup_dir.glob('data_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)

if not json_files:
    print("❌ No JSON fixture files found in backups/")
    sys.exit(1)

fixture_file = json_files[0]
print(f"\n📄 Loading: {fixture_file.name}")
print(f"   Size: {fixture_file.stat().st_size:,} bytes")

# Load and parse JSON
try:
    with open(fixture_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   Records: {len(data)}")
except Exception as e:
    print(f"❌ Error reading JSON: {e}")
    sys.exit(1)

# Try using Django's serializer
print(f"\n⏳ Loading data into PostgreSQL...")

try:
    # Using manual deserialization for better control
    print("\n   Using manual deserialization...")
    
    with open(fixture_file, 'r', encoding='utf-8') as f:
        with transaction.atomic():
            objects = serializers.deserialize('json', f, ignorenonexistent=True)
            count = 0
            for obj in objects:
                obj.save()
                count += 1
                if count % 50 == 0:
                    print(f"      Loaded {count} objects...")
            
            print(f"   ✅ Successfully loaded {count} objects")
            
except Exception as e:
    print(f"   ❌ Data loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify
print(f"\n📊 Verification:")
from django.contrib.auth.models import User
from myApp.models import Service

user_count = User.objects.count()
service_count = Service.objects.count()

print(f"   Users in PostgreSQL: {user_count}")
print(f"   Services in PostgreSQL: {service_count}")

if user_count > 0:
    print(f"\n✅ SUCCESS! Data has been loaded into PostgreSQL")
    print(f"\n📝 Next steps:")
    print(f"   1. python manage.py reset_sequences")
    print(f"   2. python manage.py check_counts")
    print(f"   3. python manage.py runserver")
else:
    print(f"\n❌ FAILED! No data was loaded")
    print(f"\n💡 Try:")
    print(f"   1. Check PostgreSQL connection")
    print(f"   2. Check for errors above")
    print(f"   3. Run: python diagnose_migration.py")

print("\n" + "=" * 70)

