# Generated manually for PageHero image_position field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0017_add_pagehero_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagehero',
            name='image_position',
            field=models.CharField(default='center center', help_text="CSS background-position (e.g., 'center center', 'center top')", max_length=50),
        ),
    ]







