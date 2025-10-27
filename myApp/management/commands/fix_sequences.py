"""
Django management command to fix PostgreSQL sequences
Usage: python manage.py fix_sequences
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL auto-increment sequences for all tables'

    def handle(self, *args, **options):
        """Reset sequences to prevent duplicate key errors"""
        
        tables = [
            'myApp_insightauditlog',
            'myApp_service',
            'myApp_insight',
            'myApp_casestudy',
            'myApp_teammember',
            'myApp_pagehero',
            'myApp_mediaasset',
            'myApp_mediaalbum',
        ]
        
        self.stdout.write(self.style.WARNING('Fixing PostgreSQL sequences...'))
        
        with connection.cursor() as cursor:
            for table in tables:
                try:
                    # Get table name without prefix for display
                    display_name = table.replace('myApp_', '')
                    
                    # Reset sequence
                    cursor.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 1),
                            true
                        );
                    """)
                    
                    result = cursor.fetchone()
                    if result:
                        new_seq = result[0]
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ {display_name}: sequence set to {new_seq}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {display_name}: {str(e)}')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n✅ All sequences fixed!'))
        self.stdout.write('You can now create/edit records without duplicate key errors.')

