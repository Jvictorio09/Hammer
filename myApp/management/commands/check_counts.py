"""
Management command to compare record counts between SQLite and PostgreSQL.

This command helps verify that data migration was successful by comparing
the number of records in each model between the source (SQLite) and
destination (PostgreSQL) databases.

Usage:
    python manage.py check_counts
"""

import sys
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.db import connections


class Command(BaseCommand):
    help = 'Compare record counts between SQLite and PostgreSQL databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='sqlite',
            help='Source database alias (default: sqlite)',
        )
        parser.add_argument(
            '--target',
            type=str,
            default='default',
            help='Target database alias (default: default)',
        )
        parser.add_argument(
            '--fail-on-mismatch',
            action='store_true',
            help='Exit with non-zero code if counts mismatch',
        )

    def handle(self, *args, **options):
        source_db = options['source']
        target_db = options['target']
        fail_on_mismatch = options['fail_on_mismatch']
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 Database Record Count Comparison'))
        self.stdout.write('=' * 70)
        
        # Check if both databases are configured
        if source_db not in settings.DATABASES:
            self.stdout.write(
                self.style.ERROR(f'❌ Source database "{source_db}" not configured!')
            )
            sys.exit(1)
        
        if target_db not in settings.DATABASES:
            self.stdout.write(
                self.style.ERROR(f'❌ Target database "{target_db}" not configured!')
            )
            sys.exit(1)
        
        self.stdout.write(f'\n📋 Configuration:')
        self.stdout.write(f'   Source DB: {source_db} ({settings.DATABASES[source_db]["ENGINE"]})')
        self.stdout.write(f'   Target DB: {target_db} ({settings.DATABASES[target_db]["ENGINE"]})')
        
        # Get all models
        all_models = apps.get_models()
        
        # Filter out models we don't want to compare
        excluded_apps = ['contenttypes', 'sessions', 'admin']
        models_to_check = [
            model for model in all_models
            if model._meta.app_label not in excluded_apps
            and not model._meta.abstract
        ]
        
        self.stdout.write(f'\n📦 Checking {len(models_to_check)} models...\n')
        
        # Track results
        results = []
        total_source = 0
        total_target = 0
        mismatches = 0
        
        # Compare counts
        for model in models_to_check:
            model_name = f'{model._meta.app_label}.{model.__name__}'
            
            try:
                # Get count from source database
                source_count = model.objects.using(source_db).count()
                total_source += source_count
                
                # Get count from target database
                target_count = model.objects.using(target_db).count()
                total_target += target_count
                
                # Check if counts match
                match = source_count == target_count
                
                if not match:
                    mismatches += 1
                
                results.append({
                    'model': model_name,
                    'source': source_count,
                    'target': target_count,
                    'match': match,
                })
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Error checking {model_name}: {str(e)}')
                )
        
        # Display results
        self.stdout.write('─' * 70)
        self.stdout.write(f'{"Model":<40} {"Source":<10} {"Target":<10} {"Status"}')
        self.stdout.write('─' * 70)
        
        for result in results:
            model_name = result['model']
            source_count = result['source']
            target_count = result['target']
            match = result['match']
            
            # Format model name (truncate if too long)
            if len(model_name) > 38:
                model_name = model_name[:35] + '...'
            
            # Color code based on match
            if match:
                if source_count == 0:
                    # Both empty - neutral
                    status = self.style.WARNING('EMPTY')
                else:
                    # Matching - good
                    status = self.style.SUCCESS('✓ OK')
            else:
                # Mismatch - bad
                status = self.style.ERROR('✗ MISMATCH')
            
            self.stdout.write(
                f'{model_name:<40} {source_count:<10} {target_count:<10} {status}'
            )
        
        self.stdout.write('─' * 70)
        self.stdout.write(f'{"TOTAL":<40} {total_source:<10} {total_target:<10}')
        self.stdout.write('─' * 70)
        
        # Summary
        self.stdout.write(f'\n📈 Summary:')
        self.stdout.write(f'   Models checked: {len(results)}')
        self.stdout.write(f'   Total records (source): {total_source:,}')
        self.stdout.write(f'   Total records (target): {total_target:,}')
        
        if mismatches == 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ All counts match! Migration successful.')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'\n⚠️  Found {mismatches} model(s) with mismatched counts!')
            )
            self.stdout.write(f'\n💡 Common causes:')
            self.stdout.write(f'   - Some models were excluded during export')
            self.stdout.write(f'   - Data was modified between export and import')
            self.stdout.write(f'   - Foreign key constraints prevented import of some records')
            
            if fail_on_mismatch:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Exiting with error due to --fail-on-mismatch flag')
                )
                sys.exit(1)
        
        self.stdout.write(f'\n📝 Next steps:')
        if mismatches == 0:
            self.stdout.write(f'   1. Remove SQLite from DATABASES in settings.py')
            self.stdout.write(f'   2. Backup db.sqlite3 and JSON fixtures to backups/')
            self.stdout.write(f'   3. Update production to use PostgreSQL')
        else:
            self.stdout.write(f'   1. Review the mismatched models above')
            self.stdout.write(f'   2. Check migration logs for errors')
            self.stdout.write(f'   3. Consider re-running the migration')

