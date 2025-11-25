# Generated manually on 2025-01-XX
# Increases field lengths for PageMetadata to support longer SEO content

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0026_blockedemail_blockedip_formsubmission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagemetadata',
            name='meta_title',
            field=models.CharField(
                blank=True,
                help_text='Page title for SEO (recommended: 50-70 characters, max 160)',
                max_length=160
            ),
        ),
        migrations.AlterField(
            model_name='pagemetadata',
            name='meta_description',
            field=models.CharField(
                blank=True,
                help_text='Meta description for SEO (recommended: 150-160 characters, max 320)',
                max_length=320
            ),
        ),
        migrations.AlterField(
            model_name='pagemetadata',
            name='og_title',
            field=models.CharField(
                blank=True,
                help_text='Open Graph title for social sharing (recommended: 50-70 characters, max 160)',
                max_length=160
            ),
        ),
        migrations.AlterField(
            model_name='pagemetadata',
            name='og_description',
            field=models.CharField(
                blank=True,
                help_text='Open Graph description for social sharing (recommended: 200-300 characters, max 400)',
                max_length=400
            ),
        ),
    ]

