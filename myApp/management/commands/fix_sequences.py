"""
Django management command to fix PostgreSQL sequences
Usage: python manage.py fix_sequences
"""

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix PostgreSQL auto-increment sequences for all tables'

    def handle(self, *args, **options):
        """Reset sequences to prevent duplicate key errors"""

        model_labels = [
            'myApp.InsightAuditLog',
            'myApp.Service',
            'myApp.Insight',
            'myApp.CaseStudy',
            'myApp.TeamMember',
            'myApp.PageHero',
            'myApp.MediaAsset',
            'myApp.MediaAlbum',
        ]

        models = []
        for label in model_labels:
            try:
                models.append(apps.get_model(label))
            except LookupError:
                self.stdout.write(self.style.WARNING(f'⚠️  Could not find model {label}'))

        if not models:
            self.stdout.write(self.style.WARNING('No models were loaded; aborting.'))
            return

        self.stdout.write(self.style.WARNING('Fixing PostgreSQL sequences...'))

        with connection.cursor() as cursor:
            for model in models:
                table = model._meta.db_table
                display_name = table.replace('myApp_', '') if table.startswith('myApp_') else table
                quoted_table = connection.ops.quote_name(table)
                pg_table_literal = f'"{table}"'

                try:
                    cursor.execute(
                        """
                        SELECT setval(
                            pg_get_serial_sequence(%s, 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 1),
                            true
                        );
                        """.format(table=quoted_table),
                        [pg_table_literal],
                    )

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

