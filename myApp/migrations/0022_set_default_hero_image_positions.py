# Generated manually to set default hero_image_position for existing services

from django.db import migrations


def set_default_positions(apps, schema_editor):
    Service = apps.get_model('myApp', 'Service')
    # Update all services that don't have a position set
    Service.objects.filter(hero_image_position__isnull=True).update(hero_image_position='50% 40%')
    Service.objects.filter(hero_image_position='').update(hero_image_position='50% 40%')
    print(f"Updated {Service.objects.count()} services with default hero_image_position")


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0021_service_hero_image_position'),
    ]

    operations = [
        migrations.RunPython(set_default_positions, reverse_code=migrations.RunPython.noop),
    ]

