"""
Management command to dump data from SQLite database to JSON fixture.

This command exports all application data from the SQLite database,
excluding system tables that shouldn't be migrated.

Usage:
    python manage.py dump_from_sqlite
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = 'Dump all data from SQLite database to a JSON fixture file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Custom output path for the JSON fixture (default: backups/data_YYYYMMDD_HHMMSS.json)',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🗄️  SQLite Data Dump Tool'))
        self.stdout.write('=' * 70)
        
        # Check if SQLite database is configured
        if 'sqlite' not in settings.DATABASES:
            self.stdout.write(
                self.style.ERROR('❌ SQLite database not configured!')
            )
            self.stdout.write(
                '   Please ensure settings.py has a "sqlite" database entry.'
            )
            sys.exit(1)
        
        # Get SQLite database path
        sqlite_db_path = settings.DATABASES['sqlite']['NAME']
        
        # Check if SQLite database file exists
        if not Path(sqlite_db_path).exists():
            self.stdout.write(
                self.style.ERROR(f'❌ SQLite database file not found: {sqlite_db_path}')
            )
            self.stdout.write(
                '   Make sure the database file exists before attempting export.'
            )
            sys.exit(1)
        
        # Check if database is readable
        if not os.access(sqlite_db_path, os.R_OK):
            self.stdout.write(
                self.style.ERROR(f'❌ Cannot read SQLite database: {sqlite_db_path}')
            )
            self.stdout.write(
                '   Check file permissions.'
            )
            sys.exit(1)
        
        # Create backups directory
        project_root = Path(settings.BASE_DIR)
        backup_dir = project_root / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Generate output filename
        if options['output']:
            output_file = Path(options['output'])
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = backup_dir / f'data_{timestamp}.json'
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write(f'\n📋 Configuration:')
        self.stdout.write(f'   Source DB: {sqlite_db_path}')
        self.stdout.write(f'   Output file: {output_file}')
        self.stdout.write(f'   Database: sqlite')
        
        # Get all app labels (for dumpdata)
        app_labels = []
        for app_config in apps.get_app_configs():
            # Skip Django's built-in apps for system tables
            if app_config.name.startswith('django.contrib'):
                # We want to include auth.User but skip other system tables
                if app_config.label == 'auth':
                    app_labels.append('auth.User')
                    app_labels.append('auth.Group')
                continue
            
            # Add custom app
            app_labels.append(app_config.label)
        
        self.stdout.write(f'\n📦 Apps to export: {", ".join(app_labels)}')
        
        # Define what to exclude
        exclude_list = [
            'contenttypes',           # Content types are auto-generated
            'auth.permission',        # Permissions are auto-generated
            'admin.logentry',         # Admin log entries (optional)
            'sessions.session',       # Session data (temporary)
        ]
        
        self.stdout.write(f'🚫 Excluding: {", ".join(exclude_list)}')
        
        # Perform the dump
        self.stdout.write(f'\n⏳ Exporting data from SQLite...')
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Call dumpdata with natural keys and specific database
                call_command(
                    'dumpdata',
                    *app_labels,
                    database='sqlite',
                    exclude=exclude_list,
                    natural_foreign=True,
                    natural_primary=True,
                    indent=2,
                    stdout=f,
                    verbosity=0,
                )
            
            # Get file size
            file_size = output_file.stat().st_size
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Data exported successfully!')
            )
            self.stdout.write(f'   Output: {output_file}')
            self.stdout.write(f'   Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)')
            
            # Count records (quick estimate by parsing JSON)
            try:
                import json
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    record_count = len(data)
                self.stdout.write(f'   Records: {record_count:,}')
            except Exception:
                pass
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Export completed successfully!')
            )
            self.stdout.write(f'\n📝 Next steps:')
            self.stdout.write(f'   1. python manage.py migrate  (on PostgreSQL)')
            self.stdout.write(f'   2. python manage.py loaddata {output_file.name}')
            self.stdout.write(f'   3. python manage.py reset_sequences')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error during export: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
            sys.exit(1)

