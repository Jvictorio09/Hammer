"""
Management command to reset PostgreSQL sequences after data import.

After loading data with loaddata, PostgreSQL sequences may be out of sync
with the actual data, causing duplicate key errors on new inserts.
This command resets all sequences to the correct values.

Usage:
    python manage.py reset_sequences
"""

import sys
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, connections
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = 'Reset all PostgreSQL sequences after data import'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database to reset sequences on (default: default)',
        )

    def handle(self, *args, **options):
        database = options['database']
        
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🔄 PostgreSQL Sequence Reset Tool'))
        self.stdout.write('=' * 70)
        
        # Check if we're using PostgreSQL
        db_engine = settings.DATABASES[database]['ENGINE']
        if 'postgresql' not in db_engine and 'psycopg' not in db_engine:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Database "{database}" is not PostgreSQL ({db_engine})'
                )
            )
            self.stdout.write(
                '   Sequence reset is only needed for PostgreSQL databases.'
            )
            self.stdout.write(
                self.style.SUCCESS('\n✅ Skipping sequence reset (not needed).')
            )
            return
        
        self.stdout.write(f'\n📋 Configuration:')
        self.stdout.write(f'   Database: {database}')
        self.stdout.write(f'   Engine: {db_engine}')
        
        # Get database connection
        conn = connections[database]
        
        # Get all models
        all_models = apps.get_models()
        
        self.stdout.write(f'\n📦 Found {len(all_models)} models to process')
        
        # Generate sequence reset SQL
        self.stdout.write(f'\n⏳ Generating sequence reset SQL...')
        
        sequence_sql = []
        models_processed = []
        
        for model in all_models:
            # Skip models without a database table
            if not hasattr(model, '_meta') or model._meta.abstract:
                continue
            
            # Get the table name
            table_name = model._meta.db_table
            
            # Check if model has an auto-incrementing primary key
            pk_field = model._meta.pk
            if pk_field and pk_field.get_internal_type() in ('AutoField', 'BigAutoField'):
                # PostgreSQL sequence naming convention: tablename_id_seq
                sequence_name = f'{table_name}_{pk_field.column}_seq'
                
                # SQL to reset the sequence to the max ID + 1
                # Use double quotes for case-sensitive table/column names in PostgreSQL
                sql = (
                    f'SELECT setval(\'{sequence_name}\', '
                    f'COALESCE((SELECT MAX("{pk_field.column}") FROM "{table_name}"), 1), '
                    f'true);'
                )
                sequence_sql.append(sql)
                models_processed.append(f'{model._meta.app_label}.{model.__name__}')
        
        if not sequence_sql:
            self.stdout.write(
                self.style.WARNING('\n⚠️  No sequences found to reset.')
            )
            return
        
        self.stdout.write(f'   Generated {len(sequence_sql)} sequence reset commands')
        
        # Execute the SQL
        self.stdout.write(f'\n⏳ Executing sequence resets...')
        
        try:
            with conn.cursor() as cursor:
                for i, sql in enumerate(sequence_sql, 1):
                    cursor.execute(sql)
                    if i % 10 == 0:
                        self.stdout.write(f'   Processed {i}/{len(sequence_sql)} sequences...')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Successfully reset {len(sequence_sql)} sequences!')
            )
            
            self.stdout.write(f'\n📊 Models processed:')
            for i, model_name in enumerate(models_processed[:10], 1):
                self.stdout.write(f'   {i}. {model_name}')
            
            if len(models_processed) > 10:
                self.stdout.write(f'   ... and {len(models_processed) - 10} more')
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Sequence reset completed successfully!')
            )
            self.stdout.write(f'\n📝 Next steps:')
            self.stdout.write(f'   1. Test your application')
            self.stdout.write(f'   2. Try creating new records to verify sequences work')
            self.stdout.write(f'   3. Run: python manage.py check_counts (to verify data)')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error resetting sequences: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
            sys.exit(1)

