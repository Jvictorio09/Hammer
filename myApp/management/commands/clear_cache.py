"""
Django management command to clear all caches
Usage: python manage.py clear_cache
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection


class Command(BaseCommand):
    help = 'Clear all Django caches and reset database connections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all caches including database connections',
        )

    def handle(self, *args, **options):
        self.stdout.write('Clearing Django cache...')
        
        try:
            # Clear default cache
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✅ Cleared default cache'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error clearing cache: {e}'))
        
        if options['all']:
            # Close all database connections
            try:
                connection.close()
                self.stdout.write(self.style.SUCCESS('✅ Closed database connections'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error closing connections: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Cache cleared successfully!'))

