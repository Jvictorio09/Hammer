#!/usr/bin/env python
"""
SEO 2025 Updates - Comprehensive Seed Script
Updates PageMetadata records with 2025-optimized SEO content.
Also seeds FAQs for services if missing.

Usage: python seed_seo_2025_updates.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from myApp.models import PageMetadata, Service, ServiceFAQ

def update_page_metadata():
    """
    Update or create PageMetadata entries with 2025-optimized SEO content.
    """
    # 2025-optimized metadata entries
    metadata_updates = [
        {
            'url_path': '/',
            'page_name': 'Home Page',
            'meta_title': 'Luxury Villa Construction, Landscaping & Interior Design in Dubai | Hammer Group',
            'meta_description': 'Hammer Group delivers luxury villa construction, landscaping, interior design and facility management in Dubai. Quiet-luxury design, end-to-end execution, and aftercare for discerning homeowners and developers.',
            'meta_keywords': 'luxury villa construction Dubai, landscaping Dubai, interior design Dubai, facility management Dubai, design and build Dubai',
            'og_title': 'Luxury Villa Construction, Landscaping & Interior Design in Dubai | Hammer Group',
            'og_description': 'Hammer Group delivers luxury villa construction, landscaping, interior design and facility management in Dubai. Quiet-luxury design, end-to-end execution, and aftercare for discerning homeowners and developers.',
        },
        {
            'url_path': '/services/',
            'page_name': 'Services Index',
            'meta_title': 'Design & Build Services Dubai | Landscape, Interior & Facility Management',
            'meta_description': 'Comprehensive design & build services in Dubai. Landscape design, interior design, facility management, and custom joinery. Expert solutions for your project.',
            'meta_keywords': 'design and build Dubai, construction services Dubai, design services Dubai, build services Dubai',
            'og_title': 'Design & Build Services Dubai | Landscape, Interior & Facility Management',
            'og_description': 'Comprehensive design & build services in Dubai. Landscape design, interior design, facility management, and custom joinery.',
        },
        {
            'url_path': '/projects/',
            'page_name': 'Projects Portfolio',
            'meta_title': 'Our Projects | Villa Construction & Design Projects in Dubai | Hammer Group',
            'meta_description': 'Explore our portfolio of luxury villa construction, landscape design, and interior design projects in Dubai. See our completed work and case studies.',
            'meta_keywords': 'villa projects Dubai, construction projects Dubai, design projects Dubai, portfolio Dubai, case studies Dubai',
            'og_title': 'Our Projects | Villa Construction & Design Projects in Dubai | Hammer Group',
            'og_description': 'Explore our portfolio of luxury villa construction, landscape design, and interior design projects in Dubai.',
        },
        {
            'url_path': '/about/',
            'page_name': 'About Us',
            'meta_title': 'About Us | Expert Design & Build Team in Dubai | Hammer Group',
            'meta_description': 'Learn about Hammer Group, Dubai\'s premier design & build company. 20+ years of experience in landscape design, interior design, and facility management.',
            'meta_keywords': 'about Hammer Group, design company Dubai, construction company Dubai, design team Dubai',
            'og_title': 'About Us | Expert Design & Build Team in Dubai | Hammer Group',
            'og_description': 'Learn about Hammer Group, Dubai\'s premier design & build company. 20+ years of experience in landscape design, interior design, and facility management.',
        },
        {
            'url_path': '/contact/',
            'page_name': 'Contact Us',
            'meta_title': 'Contact Us | Get a Quote for Your Dubai Project | Hammer Group',
            'meta_description': 'Contact Hammer Group for your design & build project in Dubai. Get expert advice, free consultations, and quotes for landscape, interior, or facility services.',
            'meta_keywords': 'contact Hammer Group, get quote Dubai, free consultation Dubai, design consultation Dubai',
            'og_title': 'Contact Us | Get a Quote for Your Dubai Project | Hammer Group',
            'og_description': 'Contact Hammer Group for your design & build project in Dubai. Get expert advice, free consultations, and quotes.',
        },
        {
            'url_path': '/insights/',
            'page_name': 'Insights & Blog',
            'meta_title': 'Design & Build Insights | Dubai Villa Construction & Landscaping Tips | Hammer',
            'meta_description': 'Expert insights on villa construction, landscape design, interior design, and facility management in Dubai. Tips, trends, and case studies from Hammer Group.',
            'meta_keywords': 'Dubai blog, construction insights, design trends, villa construction tips, landscape design tips Dubai',
            'og_title': 'Design & Build Insights | Dubai Villa Construction & Landscaping Tips | Hammer',
            'og_description': 'Expert insights on villa construction, landscape design, interior design, and facility management in Dubai.',
        },
        {
            'url_path': '/blogs/',
            'page_name': 'Blog (Legacy)',
            'meta_title': 'Design & Build Insights | Dubai Villa Construction & Landscaping Tips | Hammer',
            'meta_description': 'Expert insights on villa construction, landscape design, interior design, and facility management in Dubai. Tips, trends, and case studies from Hammer Group.',
            'meta_keywords': 'Dubai blog, construction insights, design trends, villa construction tips',
        },
        # Legacy URLs
        {
            'url_path': '/landscape/',
            'page_name': 'Landscape Design & Build',
            'meta_title': 'Landscaping Company in Dubai | Luxury Landscape Design & Build | Hammer',
            'meta_description': 'Quiet-luxury landscaping company in Dubai for villas and estates. Hammer designs and builds complete outdoor spaces: pools, pergolas, gardens, lighting and desert-friendly landscaping.',
            'meta_keywords': 'landscaping company Dubai, landscape design Dubai, pool design Dubai, garden design Dubai, villa landscaping Dubai',
        },
        {
            'url_path': '/interior/',
            'page_name': 'Interior Design & Build',
            'meta_title': 'Luxury Interior Design & Build Dubai | Villa Interiors & Joinery | Hammer Group',
            'meta_description': 'Luxury interior design and build services in Dubai. Tailored villa interiors, kitchens, wardrobes and bespoke joinery for high-end properties, from concept to turnkey handover.',
            'meta_keywords': 'interior design Dubai, villa interior design Dubai, luxury interior design Dubai, kitchen design Dubai, wardrobe design Dubai',
        },
        {
            'url_path': '/facility/',
            'page_name': 'Facility Management',
            'meta_title': 'Facility Management & Aftercare Services in Dubai | Hammer Group',
            'meta_description': 'Proactive facility management and aftercare in Dubai. Building maintenance, MEP, HVAC, cleaning and long-term property care for villas, communities and commercial assets.',
            'meta_keywords': 'facility management Dubai, property management Dubai, building maintenance Dubai, HVAC maintenance Dubai',
        },
    ]
    
    updated_count = 0
    created_count = 0
    
    print("\n" + "="*70)
    print("UPDATING PAGE METADATA (2025 SEO OPTIMIZATION)")
    print("="*70)
    
    for entry in metadata_updates:
        metadata, created = PageMetadata.objects.update_or_create(
            url_path=entry['url_path'],
            defaults={
                'page_name': entry['page_name'],
                'meta_title': entry['meta_title'],
                'meta_description': entry['meta_description'],
                'meta_keywords': entry.get('meta_keywords', ''),
                'og_title': entry.get('og_title', entry['meta_title']),
                'og_description': entry.get('og_description', entry['meta_description']),
                'is_active': True,
            }
        )
        if created:
            created_count += 1
            print(f"✅ Created: {entry['url_path']}")
        else:
            updated_count += 1
            print(f"🔄 Updated: {entry['url_path']}")
    
    print(f"\n✅ Created: {created_count} entries")
    print(f"🔄 Updated: {updated_count} entries")
    print(f"📊 Total: {created_count + updated_count} entries")
    print("="*70)


def seed_service_faqs():
    """
    Add FAQs to services if they don't have any.
    Focuses on high-intent questions for SEO and AI Overviews.
    """
    print("\n" + "="*70)
    print("SEEDING SERVICE FAQs")
    print("="*70)
    
    # Landscape FAQs
    landscape_faqs = [
        {
            'question': 'How much does villa landscaping cost in Dubai?',
            'answer': 'Landscaping costs vary based on scope, size, and materials. For a typical Dubai villa, expect AED 150,000-500,000+ for complete landscape design and build including pool, pergola, and lighting. We provide detailed quotes after site assessment.',
            'sort_order': 1
        },
        {
            'question': 'Do you handle both design and build?',
            'answer': 'Yes, Hammer Group provides end-to-end landscape design and build services. Our integrated team handles concept design, technical drawings, authority approvals, construction, and project management—all under one accountable team.',
            'sort_order': 2
        },
        {
            'question': 'Which areas in Dubai do you serve?',
            'answer': 'We serve all major areas in Dubai including Dubai Hills, Palm Jumeirah, Jumeirah, Emirates Hills, Arabian Ranches, Downtown Dubai, Business Bay, DIFC, and JVC. We also work across the UAE for high-end projects.',
            'sort_order': 3
        },
        {
            'question': 'How long does a landscape project take?',
            'answer': 'Timeline depends on scope and approvals. A complete villa landscape with pool typically takes 3-6 months from design approval to handover. We provide detailed timelines in our project proposals.',
            'sort_order': 4
        },
        {
            'question': 'Do you provide maintenance after completion?',
            'answer': 'Yes, we offer comprehensive aftercare and maintenance services through our facility management division. This includes pool maintenance, irrigation, plant care, lighting, and seasonal updates.',
            'sort_order': 5
        },
    ]
    
    # Interior FAQs
    interior_faqs = [
        {
            'question': 'How much does villa interior design cost in Dubai?',
            'answer': 'Interior design costs depend on scope, materials, and customization level. For a complete villa interior including joinery, expect AED 200,000-800,000+. We provide transparent quotes after understanding your vision and requirements.',
            'sort_order': 1
        },
        {
            'question': 'Do you handle both design and build?',
            'answer': 'Yes, Hammer Group is a full-service design-build studio. We handle concept design, technical drawings, custom joinery fabrication, installation, and project management—ensuring seamless execution from moodboard to handover.',
            'sort_order': 2
        },
        {
            'question': 'Which areas in Dubai do you serve?',
            'answer': 'We serve all major areas in Dubai including Dubai Hills, Palm Jumeirah, Jumeirah, Emirates Hills, Arabian Ranches, Downtown Dubai, Business Bay, and DIFC. We work across the UAE for luxury residential and commercial projects.',
            'sort_order': 3
        },
        {
            'question': 'Do you do custom joinery and wardrobes?',
            'answer': 'Yes, custom joinery is one of our specialties. We design and fabricate bespoke wardrobes, kitchens, built-in storage, and architectural millwork in-house, ensuring perfect fit and premium finishes.',
            'sort_order': 4
        },
        {
            'question': 'How long does an interior project take?',
            'answer': 'Timeline varies by scope. A complete villa interior typically takes 4-8 months from design approval to handover, including custom joinery fabrication. We provide detailed project schedules in our proposals.',
            'sort_order': 5
        },
    ]
    
    # Facility Management FAQs
    facility_faqs = [
        {
            'question': 'What\'s included in facility management services?',
            'answer': 'Our facility management includes hard services (MEP, HVAC, electrical, plumbing, fire safety) and soft services (cleaning, waste management, security, pest control). Pool and landscape maintenance are available as add-ons or standalone services.',
            'sort_order': 1
        },
        {
            'question': 'How quickly do you respond to emergencies?',
            'answer': 'Our 24/7 emergency response team deploys within 2 hours for critical issues like MEP failures, flooding, electrical outages, or safety hazards. We maintain standby crews and stock commonly needed parts.',
            'sort_order': 2
        },
        {
            'question': 'Do you handle permits and compliance?',
            'answer': 'Yes, we coordinate civil defense inspections, health & safety audits, and authority compliance. Our team prepares documentation, schedules visits, and ensures your facility meets all regulatory requirements.',
            'sort_order': 3
        },
        {
            'question': 'Can I customize service frequency?',
            'answer': 'Absolutely. We tailor schedules to your needs—daily cleaning, weekly HVAC checks, monthly pool servicing, or quarterly deep maintenance. You only pay for what you need.',
            'sort_order': 4
        },
        {
            'question': 'Which areas in Dubai do you serve?',
            'answer': 'We serve all major areas in Dubai including Dubai Hills, Palm Jumeirah, Jumeirah, Emirates Hills, Downtown Dubai, Business Bay, DIFC, and JVC. We also provide facility management for communities and commercial assets across the UAE.',
            'sort_order': 5
        },
    ]
    
    # Map FAQs to services
    faq_mapping = {
        'landscape-design-build': landscape_faqs,
        'interior-design-build': interior_faqs,
        'facility-management': facility_faqs,
    }
    
    created_count = 0
    skipped_count = 0
    
    for slug, faqs in faq_mapping.items():
        try:
            service = Service.objects.get(slug=slug, is_active=True)
            
            # Check if service already has FAQs
            existing_count = service.faqs.count()
            if existing_count > 0:
                print(f"⏭️  {service.title}: Already has {existing_count} FAQs (skipping)")
                skipped_count += len(faqs)
                continue
            
            # Add FAQs
            for faq_data in faqs:
                ServiceFAQ.objects.create(
                    service=service,
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    sort_order=faq_data['sort_order']
                )
                created_count += 1
            
            print(f"✅ {service.title}: Added {len(faqs)} FAQs")
            
        except Service.DoesNotExist:
            print(f"⚠️  Service '{slug}' not found (skipping FAQs)")
    
    print(f"\n✅ Created: {created_count} FAQs")
    print(f"⏭️  Skipped: {skipped_count} FAQs (already exist)")
    print("="*70)


def main():
    """Run all seeding operations."""
    print("\n" + "="*70)
    print("SEO 2025 UPDATES - COMPREHENSIVE SEED SCRIPT")
    print("="*70)
    print("\nThis script will:")
    print("1. Update PageMetadata records with 2025-optimized SEO content")
    print("2. Add FAQs to services if they don't have any")
    print("\nStarting...\n")
    
    # Update metadata
    update_page_metadata()
    
    # Seed FAQs
    seed_service_faqs()
    
    print("\n" + "="*70)
    print("✅ SEO 2025 UPDATES COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review updated metadata at /dashboard/metadata/")
    print("2. Review service FAQs at /dashboard/services/")
    print("3. Test schema markup with Google Rich Results Test")
    print("4. Monitor search performance in Google Search Console")
    print("\n")


if __name__ == '__main__':
    main()

