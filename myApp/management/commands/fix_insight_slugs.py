"""
Django management command to fix invalid insight slugs
Usage: python manage.py fix_insight_slugs
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from myApp.models import Insight


class Command(BaseCommand):
    help = 'Fix invalid insight slugs (like "-") by regenerating them from titles'

    def handle(self, *args, **options):
        """Fix all insights with invalid slugs"""
        
        self.stdout.write(self.style.WARNING('Fixing invalid insight slugs...'))
        
        # Check all insights for invalid slugs
        all_insights = Insight.objects.all()
        fixed_count = 0
        
        for insight in all_insights:
            # Check if slug is invalid
            if not insight.slug or insight.slug.strip() == '-' or not insight.slug.strip() or len(insight.slug.strip()) < 2:
                if not insight.title:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Insight ID {insight.pk}: No title, skipping')
                    )
                    continue
                
                # Generate base slug from title
                base_slug = slugify(insight.title)[:220]
                if not base_slug:
                    base_slug = f"insight-{insight.pk}"
                
                # Ensure uniqueness
                original_slug = base_slug
                counter = 1
                
                existing = Insight.objects.filter(slug=base_slug).exclude(pk=insight.pk)
                while existing.exists():
                    counter += 1
                    max_base_length = 220 - len(str(counter)) - 1
                    base_slug = f"{original_slug[:max_base_length]}-{counter}"
                    existing = Insight.objects.filter(slug=base_slug).exclude(pk=insight.pk)
                    
                    if counter > 10000:
                        break
                
                old_slug = insight.slug
                insight.slug = base_slug
                insight.save(update_fields=['slug'])
                
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Fixed: "{insight.title[:50]}..." '
                        f'(ID: {insight.pk}, old: "{old_slug}" → new: "{base_slug}")'
                    )
                )
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No invalid slugs found. All insights have valid slugs.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Fixed {fixed_count} insight slug(s)!')
            )
            self.stdout.write('All slugs are now generated from titles and are unique.')

