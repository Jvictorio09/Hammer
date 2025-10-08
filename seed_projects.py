#!/usr/bin/env python3
"""
Seed Case Studies / Projects for any Service

Usage:
  python seed_projects.py --settings myProject.settings --service-slug landscape-design-build --wipe
  python seed_projects.py --settings myProject.settings --service-id 1
"""
import os
import sys
import argparse
from datetime import date

# Django setup
def setup_django(settings_module: str | None):
    if settings_module:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"[!] Django setup failed: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Seed Case Studies / Projects for a Service")
    parser.add_argument("--settings", help="Django settings module (e.g., myProject.settings)")
    parser.add_argument("--service-id", type=int, help="Service ID to attach case studies to")
    parser.add_argument("--service-slug", help="Service slug to attach case studies to")
    parser.add_argument("--wipe", action="store_true", help="Wipe existing case studies first")
    args = parser.parse_args()

    setup_django(args.settings)

    from django.db import transaction
    from myApp.models import Service, CaseStudy

    def upsert(instance, data: dict, fields: list[str]):
        changed = False
        for f in fields:
            if hasattr(instance, f):
                old = getattr(instance, f, None)
                new = data.get(f, old)
                if old != new:
                    setattr(instance, f, new)
                    changed = True
        if changed:
            instance.save()
        return changed

    # CASE STUDIES DATA
    CASE_STUDIES = [
        {
            "title": "Villa Retreat - Emirates Hills",
            "hero_image_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=1600&auto=format&fit=crop",
            "summary": "A contemporary outdoor sanctuary with native planting, custom pool, and architectural lighting designed for year-round outdoor living.",
            "description": """This 8,500 sqft landscape transformation combines sustainable design with luxury execution.

The Challenge:
- Hot, arid climate requiring drought-smart solutions
- Need for evening entertainment spaces
- Privacy from neighboring properties

Our Solution:
- Native planting palette with drip irrigation zones
- 15m infinity pool with underwater LED scenes
- Pergola structure with automated louvres
- Three-layer lighting design (path, feature, ambient)
- Acoustic screening with Ficus nitida hedging

The project showcases how thoughtful material selection and integrated MEP coordination deliver spaces that perform beautifully with minimal maintenance.""",
            "completion_date": date(2023, 11, 15),
            "scope": "Design + Build + Pool",
            "size_label": "8,500 sqft",
            "timeline_label": "7 months",
            "status_label": "Completed",
            "tags_csv": "Landscape, Pool, Lighting, Native Planting",
            "is_featured": True,
            "sort_order": 1,
        },
        {
            "title": "Courtyard Oasis - Arabian Ranches",
            "hero_image_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=1600&auto=format&fit=crop",
            "summary": "Intimate courtyard garden featuring water features, custom pergola, and curated planting for a serene outdoor escape.",
            "description": """A 3,200 sqft courtyard transformation that maximizes space efficiency while creating distinct zones for dining, lounging, and contemplation.

Key Features:
- Sculpted water feature with natural stone cladding
- Timber pergola with integrated misting system
- Low-maintenance planting with seasonal color
- Concealed uplighting for evening ambience

Delivered on schedule with weekly progress reviews and transparent communication throughout.""",
            "completion_date": date(2024, 3, 20),
            "scope": "Design + Build",
            "size_label": "3,200 sqft",
            "timeline_label": "4 months",
            "status_label": "Completed",
            "tags_csv": "Landscape, Water Features, Pergola",
            "is_featured": False,
            "sort_order": 2,
        },
        {
            "title": "Modern Minimalist Garden - Dubai Hills",
            "hero_image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=2000&q=80",
            "thumb_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
            "full_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80",
            "summary": "Clean lines, structural planting, and water-wise species create a sophisticated, low-maintenance outdoor space.",
            "description": """Minimalist landscape design emphasizing form, texture, and sustainability.

Design Approach:
- Architectural massing with native grasses and succulents
- Geometric hardscape in limestone and corten steel
- Drip irrigation with smart controller
- Minimal lawn area (reduced to 20% of total site)

Result: A garden that looks sharp year-round with 40% less water consumption than traditional landscapes.""",
            "completion_date": date(2024, 1, 10),
            "scope": "Design + Build",
            "size_label": "5,100 sqft",
            "timeline_label": "5 months",
            "status_label": "Completed",
            "tags_csv": "Landscape, Sustainable, Minimalist",
            "is_featured": False,
            "sort_order": 3,
        },
        {
            "title": "Rooftop Garden - Business Bay",
            "hero_image_url": "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=1600&auto=format&fit=crop",
            "summary": "High-rise outdoor entertaining space with wind-tolerant planting and modular furniture zones.",
            "description": """Converting a bare rooftop into a premium outdoor amenity required careful wind analysis and structural coordination.

Delivered:
- Wind-resistant planting in custom planters with irrigation
- Modular seating zones with shade structures
- Deck system with concealed drainage
- Ambient lighting integrated into railings

The space now serves as a signature feature for the building's residents.""",
            "completion_date": date(2023, 8, 30),
            "scope": "Design + Build",
            "size_label": "2,800 sqft",
            "timeline_label": "3 months",
            "status_label": "Completed",
            "tags_csv": "Landscape, Rooftop, Commercial",
            "is_featured": False,
            "sort_order": 4,
        },
        {
            "title": "Architectural Lighting Showcase",
            "hero_image_url": "https://images.unsplash.com/photo-1542744173-05336fcc7ad4?auto=format&fit=crop&w=2000&q=80",
            "thumb_url": "https://images.unsplash.com/photo-1542744173-05336fcc7ad4?auto=format&fit=crop&w=800&q=80",
            "full_url": "https://images.unsplash.com/photo-1542744173-05336fcc7ad4?auto=format&fit=crop&w=1600&q=80",
            "summary": "Layered evening scenes that celebrate landscape architecture without glare or light pollution.",
            "description": """A comprehensive lighting design demonstrating our three-layer approach to outdoor illumination.

Lighting Layers:
1. Path & Safety - Low-level fixtures with warm color temperature
2. Feature Lighting - Uplights for trees and architectural elements
3. Ambient Glow - Concealed cove lighting in pergolas and water features

All zones are separately controlled with preset scenes for different occasions. The result is cinematic atmosphere with practical functionality.""",
            "completion_date": date(2024, 2, 5),
            "scope": "Lighting Design + Install",
            "size_label": "6,200 sqft",
            "timeline_label": "2 months",
            "status_label": "Completed",
            "tags_csv": "Lighting, Landscape, Smart Controls",
            "is_featured": False,
            "sort_order": 5,
        },
    ]

    # Find service
    svc = None
    if args.service_id:
        svc = Service.objects.filter(id=args.service_id).first()
        if not svc:
            print(f"[!] No Service found with id={args.service_id}")
            sys.exit(1)
    elif args.service_slug:
        svc = Service.objects.filter(slug=args.service_slug).first()
        if not svc:
            print(f"[!] No Service found with slug='{args.service_slug}'")
            sys.exit(1)
    else:
        print("[!] Please specify --service-id or --service-slug")
        sys.exit(1)

    print(f"[i] Seeding Projects for Service: {svc.title}")

    with transaction.atomic():
        if args.wipe:
            print("[!] Wiping existing case studies…")
            svc.case_studies.all().delete()

        # Seed Case Studies
        for i, cs in enumerate(CASE_STUDIES, start=1):
            obj, created = CaseStudy.objects.get_or_create(service=svc, title=cs["title"])
            changed = upsert(
                obj,
                {
                    "hero_image_url": cs["hero_image_url"],
                    "thumb_url": cs["thumb_url"],
                    "full_url": cs["full_url"],
                    "summary": cs["summary"],
                    "description": cs["description"],
                    "completion_date": cs["completion_date"],
                    "scope": cs["scope"],
                    "size_label": cs["size_label"],
                    "timeline_label": cs["timeline_label"],
                    "status_label": cs["status_label"],
                    "tags_csv": cs["tags_csv"],
                    "is_featured": cs["is_featured"],
                    "sort_order": cs["sort_order"],
                },
                [
                    "hero_image_url", "thumb_url", "full_url", "summary", "description",
                    "completion_date", "scope", "size_label", "timeline_label", "status_label",
                    "tags_csv", "is_featured", "sort_order"
                ],
            )
            status = 'Created' if created else ('Updated' if changed else 'Kept')
            print(f" [{status}] Case Study • {obj.title}")

    print("\n✔ Seed complete!")
    print(f"→ Visit /services/{svc.slug}/ to see the projects gallery")
    print(f"→ Case Studies created: {svc.case_studies.count()}")

if __name__ == "__main__":
    main()

