#!/usr/bin/env python
"""
Standalone script to seed PageMetadata entries.
Run this AFTER running migrations to create the PageMetadata table.

Usage: python seed_metadata.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from myApp.models import PageMetadata

def seed_metadata():
    """
    Create PageMetadata entries for all existing public URLs.
    These are starter entries that can be customized via the dashboard.
    """
    # Define all static URLs with their metadata
    metadata_entries = [
        {
            'url_path': '/',
            'page_name': 'Home Page',
            'meta_title': 'Luxury Villa Construction, Landscaping & Interior Design in Dubai | Hammer Group',
            'meta_description': 'Premier construction, landscaping, and interior design services in Dubai. 20+ years transforming visions into exceptional living spaces.',
            'meta_keywords': 'Dubai construction, villa construction, landscaping Dubai, interior design Dubai, luxury homes, property development UAE',
        },
        {
            'url_path': '/about/',
            'page_name': 'About Us',
            'meta_title': 'About Hammer Group | Dubai Luxury Construction Experts',
            'meta_description': '20+ years delivering exceptional construction, landscaping, and interior design in Dubai. Meet our team of specialists transforming Dubai\'s luxury landscape.',
            'meta_keywords': 'about us, Dubai construction company, luxury builders, landscaping experts, team Dubai',
        },
        {
            'url_path': '/aboutus/',
            'page_name': 'About Us (Legacy)',
            'meta_title': 'About Hammer Group | Dubai Luxury Construction Experts',
            'meta_description': '20+ years delivering exceptional construction, landscaping, and interior design in Dubai. Meet our team of specialists.',
            'meta_keywords': 'about us, Dubai construction company, team Dubai',
        },
        {
            'url_path': '/contact/',
            'page_name': 'Contact Us',
            'meta_title': 'Contact Us | Hammer Group Dubai',
            'meta_description': 'Get in touch with Hammer Group for luxury construction, landscaping, and interior design services in Dubai. Let\'s discuss your vision.',
            'meta_keywords': 'contact, Dubai construction contact, get quote, consultation Dubai',
        },
        {
            'url_path': '/services/',
            'page_name': 'Services Index',
            'meta_title': 'Our Services | Luxury Construction, Landscaping & Interior Design Dubai',
            'meta_description': 'Comprehensive construction, landscaping, and interior design services in Dubai. From concept to completion, we deliver excellence.',
            'meta_keywords': 'Dubai construction services, landscaping services, interior design services, facility management',
        },
        {
            'url_path': '/landscape/',
            'page_name': 'Landscape Design & Build',
            'meta_title': 'Landscape Design & Build Dubai | Hammer Group',
            'meta_description': 'Premium landscape design & build in Dubai. Native planting, custom pools, pergolas, and architectural lighting by one expert team.',
            'meta_keywords': 'landscape design Dubai, pool design, outdoor landscaping, garden design UAE, pergola construction',
        },
        {
            'url_path': '/landscape',
            'page_name': 'Landscape (No Slash)',
            'meta_title': 'Landscape Design & Build Dubai | Hammer Group',
            'meta_description': 'Premium landscape design & build in Dubai. Native planting, custom pools, pergolas, and architectural lighting by one expert team.',
            'meta_keywords': 'landscape design Dubai, pool design, outdoor landscaping',
        },
        {
            'url_path': '/landscaping/',
            'page_name': 'Landscaping Services',
            'meta_title': 'Professional Landscaping Services Dubai | Hammer Group',
            'meta_description': 'Expert landscaping services in Dubai. Creating stunning outdoor spaces with native planting, pools, and architectural lighting.',
            'meta_keywords': 'landscaping Dubai, landscape services, garden design, outdoor spaces',
        },
        {
            'url_path': '/interior/',
            'page_name': 'Interior Design & Build',
            'meta_title': 'Interior Design & Build Dubai | Luxury Home Interiors | Hammer Group',
            'meta_description': 'Transform your space with premium interior design & build services in Dubai. From concept to installation, delivering exceptional results.',
            'meta_keywords': 'interior design Dubai, home interiors, luxury design, residential fit-out, commercial design',
        },
        {
            'url_path': '/interior',
            'page_name': 'Interior (No Slash)',
            'meta_title': 'Interior Design & Build Dubai | Hammer Group',
            'meta_description': 'Transform your space with premium interior design & build services in Dubai.',
            'meta_keywords': 'interior design Dubai, home interiors, luxury design',
        },
        {
            'url_path': '/facility/',
            'page_name': 'Facility Management',
            'meta_title': 'Facility Management & Aftercare Dubai | Hammer Group',
            'meta_description': 'Professional facility management and aftercare services in Dubai. Keeping your properties in pristine condition with dedicated maintenance.',
            'meta_keywords': 'facility management Dubai, property maintenance, aftercare services, building maintenance UAE',
        },
        {
            'url_path': '/facility',
            'page_name': 'Facility (No Slash)',
            'meta_title': 'Facility Management Dubai | Hammer Group',
            'meta_description': 'Professional facility management and aftercare services in Dubai.',
            'meta_keywords': 'facility management Dubai, property maintenance',
        },
        {
            'url_path': '/projects/',
            'page_name': 'Projects Portfolio',
            'meta_title': 'Our Projects | Luxury Construction & Design Portfolio Dubai | Hammer Group',
            'meta_description': 'Browse our portfolio of luxury construction, landscaping, and interior design projects in Dubai. See how we transform spaces.',
            'meta_keywords': 'Dubai projects, construction portfolio, case studies, luxury homes Dubai, completed projects',
        },
        {
            'url_path': '/projects',
            'page_name': 'Projects (No Slash)',
            'meta_title': 'Our Projects | Portfolio Dubai | Hammer Group',
            'meta_description': 'Browse our portfolio of luxury construction and design projects in Dubai.',
            'meta_keywords': 'Dubai projects, portfolio, case studies',
        },
        {
            'url_path': '/insights/',
            'page_name': 'Insights & Blog',
            'meta_title': 'Insights & Latest Updates | Dubai Construction & Design Blog | Hammer Group',
            'meta_description': 'Stay updated with the latest insights on construction, landscaping, and interior design trends in Dubai. Expert tips and industry news.',
            'meta_keywords': 'Dubai blog, construction insights, design trends, industry news UAE, interior design tips',
        },
        {
            'url_path': '/blogs/',
            'page_name': 'Blog (Legacy)',
            'meta_title': 'Blog | Latest Construction & Design Insights Dubai | Hammer Group',
            'meta_description': 'Read our latest blog posts about construction, landscaping, and interior design in Dubai. Expert tips and industry insights.',
            'meta_keywords': 'blog Dubai, construction blog, design insights, industry news',
        },
        {
            'url_path': '/villas',
            'page_name': 'Villas',
            'meta_title': 'Luxury Villas Dubai | Custom Villa Construction | Hammer Group',
            'meta_description': 'Luxury custom villa construction and design in Dubai. Creating exceptional residential experiences from concept to completion.',
            'meta_keywords': 'villa construction Dubai, luxury villas, custom homes UAE, villa design',
        },
        # Legacy service URLs
        {
            'url_path': '/services/landscaping/',
            'page_name': 'Landscaping Service',
            'meta_title': 'Professional Landscaping Services Dubai | Hammer Group',
            'meta_description': 'Expert landscaping services in Dubai. Creating stunning outdoor spaces with native planting, pools, and architectural lighting.',
            'meta_keywords': 'landscaping Dubai, landscape services, garden design, outdoor spaces',
        },
        {
            'url_path': '/services/landscape/',
            'page_name': 'Landscape Service',
            'meta_title': 'Landscape Design & Build Dubai | Hammer Group',
            'meta_description': 'Premium landscape design & build in Dubai. Native planting, custom pools, pergolas, and architectural lighting.',
            'meta_keywords': 'landscape design Dubai, pool design, outdoor landscaping',
        },
        {
            'url_path': '/services/maintenance/',
            'page_name': 'Maintenance Service',
            'meta_title': 'Facility Management & Maintenance Dubai | Hammer Group',
            'meta_description': 'Professional facility management and maintenance services in Dubai. Keeping your properties in pristine condition.',
            'meta_keywords': 'facility management Dubai, property maintenance, building maintenance',
        },
        {
            'url_path': '/services/swimming-pools/',
            'page_name': 'Swimming Pools Service',
            'meta_title': 'Custom Swimming Pool Design & Construction Dubai | Hammer Group',
            'meta_description': 'Design and build custom swimming pools for luxury properties in Dubai. Expert pool construction and installation.',
            'meta_keywords': 'pool design Dubai, swimming pool construction, custom pools UAE',
        },
        {
            'url_path': '/services/commercial-fit-out/',
            'page_name': 'Commercial Fit-Out Service',
            'meta_title': 'Commercial Fit-Out Services Dubai | Hammer Group',
            'meta_description': 'Professional commercial interior fit-out services in Dubai. Transforming commercial spaces with quality craftsmanship.',
            'meta_keywords': 'commercial fit-out Dubai, office design, retail interiors, commercial spaces',
        },
        {
            'url_path': '/interior/residential-fit-out-company-in-dubai/',
            'page_name': 'Residential Fit-Out Company',
            'meta_title': 'Residential Fit-Out Company Dubai | Interior Design | Hammer Group',
            'meta_description': 'Leading residential fit-out company in Dubai. Complete interior design and fit-out services for luxury homes.',
            'meta_keywords': 'residential fit-out Dubai, home interiors, interior fit-out company',
        },
        {
            'url_path': '/landscape/landscape-design-development-company/',
            'page_name': 'Landscape Design Company',
            'meta_title': 'Landscape Design Development Company Dubai | Hammer Group',
            'meta_description': 'Premier landscape design and development company in Dubai. Creating stunning outdoor environments.',
            'meta_keywords': 'landscape design company Dubai, landscape development, outdoor design',
        },
    ]
    
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*70)
    print("SEEDING PAGE METADATA")
    print("="*70)
    
    for entry in metadata_entries:
        # Check if entry already exists (for idempotent running)
        if not PageMetadata.objects.filter(url_path=entry['url_path']).exists():
            PageMetadata.objects.create(
                url_path=entry['url_path'],
                page_name=entry['page_name'],
                meta_title=entry['meta_title'],
                meta_description=entry['meta_description'],
                meta_keywords=entry['meta_keywords'],
                is_active=True,
            )
            created_count += 1
        else:
            skipped_count += 1
    
    print(f"\n✅ Created: {created_count} entries")
    print(f"⏭️  Skipped: {skipped_count} entries (already exist)")
    print(f"📊 Total: {created_count + skipped_count} entries")
    print("="*70)
    print("\nMetadata seeding complete!")

if __name__ == '__main__':
    seed_metadata()

