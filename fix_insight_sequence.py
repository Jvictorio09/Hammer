#!/usr/bin/env python
"""
Fix PostgreSQL sequence for Insight table
Run this script from the myProject directory: python fix_insight_sequence.py
"""

import os
import sys
import django

# Setup Django - we're already in myProject directory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from django.apps import apps
from django.db import connection

def fix_sequence():
    """Reset the sequence for Insight to the correct value"""
    Insight = apps.get_model('myApp', 'Insight')
    table = Insight._meta.db_table
    quoted_table = connection.ops.quote_name(table)
    pg_table_literal = f'"{table}"'

    with connection.cursor() as cursor:
        # Get the current max ID
        cursor.execute("""
            SELECT COALESCE(MAX(id), 0) + 1 
            FROM {};
        """.format(quoted_table))
        next_id = cursor.fetchone()[0]
        
        print(f"Current max ID in table: {next_id - 1}")
        print(f"Setting sequence to: {next_id}")
        
        # Reset the sequence
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence(%s, 'id'),
                COALESCE((SELECT MAX(id) FROM {}), 1),
                true
            );
        """.format(quoted_table), [pg_table_literal])
        
        result = cursor.fetchone()[0]
        print(f"✅ Sequence reset successfully to: {result}")
        print("\nYou can now create insights without errors!")

if __name__ == '__main__':
    try:
        fix_sequence()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)





