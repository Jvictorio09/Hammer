# Generated manually for PageHero model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0016_add_gallery_urls_to_case_study'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageHero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.CharField(choices=[('home', 'Home'), ('about', 'About'), ('services', 'Services'), ('projects', 'Projects'), ('insights', 'Insights'), ('contact', 'Contact')], db_index=True, help_text='Which page this hero applies to', max_length=50, unique=True)),
                ('title', models.CharField(help_text='Internal title for identification', max_length=200)),
                ('eyebrow', models.CharField(blank=True, help_text="Small text above headline (e.g., 'Dubai • Design & Build')", max_length=100)),
                ('headline', models.CharField(help_text='Main hero headline', max_length=250)),
                ('subtext', models.TextField(blank=True, help_text='Supporting text below headline')),
                ('hero_image_url', models.URLField(blank=True, help_text='Cloudinary URL for hero background image')),
                ('buttons', models.JSONField(blank=True, default=list, help_text='Array of button objects: [{text, url, style}, ...]')),
                ('pills', models.JSONField(blank=True, default=list, help_text="Array of pill text: ['pill 1', 'pill 2', ...]")),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Set to false to temporarily disable')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Page Hero',
                'verbose_name_plural': 'Page Heroes',
                'ordering': ['page'],
            },
        ),
    ]

