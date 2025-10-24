"""
Seed script to initialize default hero content for pages.
Run this after applying the PageHero migration:
    python seed_heroes.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from myApp.models import PageHero

def seed_heroes():
    """Create default hero content for each page"""
    
    heroes_data = [
        {
            'page': 'home',
            'title': 'Home Hero - Luxury Landscaping & Design',
            'eyebrow': 'Dubai • Design & Build • End-to-End',
            'headline': 'Luxury landscaping, Interior Design and villa construction in Dubai',
            'subtext': 'Your one accountable partner to plan, design, build and maintain luxury residential and commercial spaces so you get certainty on quality, cost and timelines.',
            'hero_image_url': 'https://res.cloudinary.com/dstlxtvar/image/upload/f_auto,q_auto/v1759757960/projects/duabi_hills%2C_parkways/IMG_0783-Enhanced-NR.jpg',
            'buttons': [
                {
                    'text': 'Explore Services',
                    'url': '#services',
                    'style': 'outline'
                },
                {
                    'text': 'Request Consultation',
                    'url': '#contact',
                    'style': 'filled',
                    'icon': 'fa-solid fa-calendar-check'
                }
            ],
            'pills': [
                'Single point of accountability',
                'Fixed milestones & transparent reporting',
                'Aftercare & facility management'
            ],
            'is_active': True
        },
        {
            'page': 'about',
            'title': 'About Hero - Our Story',
            'eyebrow': 'Dubai Design Excellence',
            'headline': 'Built on craftsmanship, delivered with precision',
            'subtext': 'Since 2005, we\'ve brought together landscape, interiors, and build expertise under one roof—eliminating hand-offs and delivering certainty on quality, cost, and timelines.',
            'hero_image_url': 'https://res.cloudinary.com/dstlxtvar/image/upload/f_auto,q_auto/v1759757960/projects/duabi_hills%2C_parkways/IMG_0783-Enhanced-NR.jpg',
            'buttons': [
                {
                    'text': 'Meet Our Team',
                    'url': '#team',
                    'style': 'outline'
                },
                {
                    'text': 'View Projects',
                    'url': '/projects/',
                    'style': 'filled'
                }
            ],
            'pills': [
                '20+ years in Dubai',
                '1000+ projects delivered',
                'End-to-end accountability'
            ],
            'is_active': False  # Disabled by default, enable when ready
        },
        {
            'page': 'services',
            'title': 'Services Hero - What We Do',
            'eyebrow': 'Complete Design & Build Solutions',
            'headline': 'From concept to completion, we handle everything',
            'subtext': 'Landscape design, interior fit-outs, joinery, marble work, and facility management—all delivered by one expert team.',
            'hero_image_url': 'https://res.cloudinary.com/dstlxtvar/image/upload/f_auto,q_auto/v1759757960/projects/duabi_hills%2C_parkways/IMG_0783-Enhanced-NR.jpg',
            'buttons': [
                {
                    'text': 'Browse Services',
                    'url': '#services',
                    'style': 'outline'
                },
                {
                    'text': 'Get a Quote',
                    'url': '/contact/',
                    'style': 'filled'
                }
            ],
            'pills': [
                'Integrated approach',
                'Premium materials',
                'On-time delivery'
            ],
            'is_active': False
        },
        {
            'page': 'projects',
            'title': 'Projects Hero - Our Work',
            'eyebrow': 'Our Portfolio',
            'headline': 'Signature Projects',
            'subtext': 'Explore our curated collection of exceptional work across architecture, interiors, and design.',
            'hero_image_url': '',  # Leave empty to use gradient background by default
            'buttons': [],  # Projects page doesn't need CTA buttons in hero
            'pills': [],
            'is_active': False  # Activate from dashboard when ready
        },
        {
            'page': 'insights',
            'title': 'Insights Hero - Industry Knowledge',
            'eyebrow': 'Industry Insights',
            'headline': 'Design trends, materials, and best practices',
            'subtext': 'Expert perspectives on luxury design, construction techniques, and maintaining high-end properties in Dubai\'s climate.',
            'hero_image_url': 'https://res.cloudinary.com/dstlxtvar/image/upload/f_auto,q_auto/v1759757960/projects/duabi_hills%2C_parkways/IMG_0783-Enhanced-NR.jpg',
            'buttons': [
                {
                    'text': 'Browse Articles',
                    'url': '#insights',
                    'style': 'outline'
                }
            ],
            'pills': [
                'Design trends',
                'Material guides',
                'Maintenance tips'
            ],
            'is_active': False
        },
        {
            'page': 'contact',
            'title': 'Contact Hero - Get in Touch',
            'eyebrow': 'Let\'s Talk',
            'headline': 'Start your project with a consultation',
            'subtext': 'Share your vision and we\'ll provide a clear roadmap—scope, timeline, and transparent pricing.',
            'hero_image_url': 'https://res.cloudinary.com/dstlxtvar/image/upload/f_auto,q_auto/v1759757960/projects/duabi_hills%2C_parkways/IMG_0783-Enhanced-NR.jpg',
            'buttons': [
                {
                    'text': 'Schedule Consultation',
                    'url': '#contact-form',
                    'style': 'filled',
                    'icon': 'fa-solid fa-calendar-check'
                }
            ],
            'pills': [
                'Free consultation',
                'Quick response',
                'Transparent pricing'
            ],
            'is_active': False
        }
    ]
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    for hero_data in heroes_data:
        page = hero_data['page']
        try:
            hero, created = PageHero.objects.update_or_create(
                page=page,
                defaults=hero_data
            )
            if created:
                print(f"✓ Created hero for '{hero.get_page_display()}' page")
                created_count += 1
            else:
                print(f"↻ Updated hero for '{hero.get_page_display()}' page")
                updated_count += 1
        except Exception as e:
            print(f"✗ Error with '{page}' hero: {str(e)}")
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Hero Seeding Summary:")
    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"{'='*60}\n")
    
    print("Note: Only the 'home' hero is active by default.")
    print("You can activate others from the dashboard at /dashboard/heroes/")


if __name__ == '__main__':
    print("Seeding page heroes...")
    print("-" * 60)
    seed_heroes()

