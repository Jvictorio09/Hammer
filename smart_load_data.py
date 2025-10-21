#!/usr/bin/env python
"""
Smart data loader - skips duplicates and handles errors gracefully
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

from django.core import serializers
from django.db import transaction, IntegrityError

print("=" * 70)
print("🧠 SMART DATA LOADER (Skip Duplicates)")
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

print(f"\n⏳ Loading data into PostgreSQL (skipping duplicates)...")

success_count = 0
skip_count = 0
error_count = 0
errors = []

try:
    with open(fixture_file, 'r', encoding='utf-8') as f:
        objects = serializers.deserialize('json', f, ignorenonexistent=True)
        
        for obj in objects:
            try:
                # Try to save each object individually (not in a transaction)
                obj.save()
                success_count += 1
                
                if success_count % 50 == 0:
                    print(f"   ✓ Loaded {success_count} objects (skipped {skip_count})...")
                    
            except IntegrityError as e:
                # Skip duplicates
                skip_count += 1
                if 'duplicate key' in str(e) or 'UNIQUE constraint' in str(e):
                    # This is expected for duplicates, just skip
                    pass
                else:
                    # Other integrity errors
                    error_count += 1
                    error_msg = f"{obj.object.__class__.__name__}: {str(e)[:100]}"
                    if error_msg not in errors:
                        errors.append(error_msg)
                        
            except Exception as e:
                # Other errors
                error_count += 1
                error_msg = f"{obj.object.__class__.__name__}: {str(e)[:100]}"
                if error_msg not in errors:
                    errors.append(error_msg)
        
        print(f"\n✅ Data loading completed!")
        print(f"   Successfully loaded: {success_count} objects")
        print(f"   Skipped (duplicates): {skip_count} objects")
        
        if error_count > 0:
            print(f"   ⚠️  Errors: {error_count} objects")
            if errors:
                print(f"\n   Sample errors:")
                for err in errors[:5]:
                    print(f"      - {err}")
                    
except Exception as e:
    print(f"   ❌ Fatal error: {e}")
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
    print(f"   2. python diagnose_migration.py")
    print(f"   3. python manage.py runserver")
else:
    print(f"\n⚠️  Warning: No users found in PostgreSQL")
    print(f"   Check the errors above")

print("\n" + "=" * 70)

