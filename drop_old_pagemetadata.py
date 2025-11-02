#!/usr/bin/env python
"""
One-time script to drop the old PageMetadata table that got left behind.
Run this once before running migrations.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from django.db import connection

print("="*70)
print("DROPPING OLD PAGEMETADATA TABLE")
print("="*70)

with connection.cursor() as cursor:
    print("\nDropping table if it exists...")
    # Try both uppercase and lowercase (PostgreSQL is case-sensitive in quotes)
    cursor.execute("DROP TABLE IF EXISTS myApp_pagemetadata CASCADE;")
    cursor.execute('DROP TABLE IF EXISTS "myApp_pagemetadata" CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS "myapp_pagemetadata" CASCADE;')
    cursor.execute('DROP TABLE IF EXISTS myapp_pagemetadata CASCADE;')
    print("✓ Table dropped (tried all variants)")

print("\n" + "="*70)
print("✅ Done! Now run: python manage.py migrate")
print("="*70)

