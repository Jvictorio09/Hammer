#!/usr/bin/env python3
"""
Seed a complete 'Landscape Design & Build' Service page with rich, production-level content.

Usage:
  python seed_landscape.py --settings myProject.settings
  python seed_landscape.py --settings myProject.settings --wipe
  python seed_landscape.py --settings myProject.settings --title "Landscape Design & Build" --slug "landscape-design-build"

Notes:
- Idempotent: existing rows are updated (unless --wipe).
- Mirrors the live page content you shared (hero, metrics, capabilities, steps, BA pairs, projects, FAQs).
"""
# seed_landscape.py
import os
import sys
import argparse
from datetime import date

# -----------------------------
# Django setup (optional --settings)
# -----------------------------
def setup_django(settings_module: str | None):
    if settings_module:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    try:
        import django  # noqa
        django.setup()
    except Exception as e:
        print(f"[!] Django setup failed: {e}")
        raise

# -----------------------------
# Main seeding routine
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Seed Case Studies / Projects for a Service")
    parser.add_argument("--settings", help="Django settings module (e.g., myProject.settings)")
    parser.add_argument("--service-id", type=int, help="Service ID to attach case studies to")
    parser.add_argument("--service-slug", help="Service slug to attach case studies to")
    parser.add_argument("--wipe", action="store_true", help="Wipe existing related rows first")
    args = parser.parse_args()

    setup_django(args.settings)

    # Imports after Django setup
    from django.db import transaction
    from myApp.models import (
        Service,
        ServiceFeature,
        ServiceEditorialImage,
        ServiceProjectImage,  # keep for backwards compatibility
        ServiceCapability,
        ServiceProcessStep,
        ServiceMetric,
        ServiceFAQ,
        ServicePartnerBrand,
        ServiceTestimonial,
        Insight,
        CaseStudy,
    )

    # Optional gallery model
    try:
        from myApp.models import CaseStudyImage  # FK to CaseStudy, related_name="images"
        HAS_CS_IMAGE = True
    except Exception:
        HAS_CS_IMAGE = False

    # -----------------------------
    # Helpers
    # -----------------------------
    UNSPLASH_16x9 = [
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1494526585095-c41746248156?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1600&auto=format&fit=crop",
    ]

    def five_dummy_images(seed_hint: str):
        out = []
        for i, url in enumerate(UNSPLASH_16x9, start=1):
            out.append({
                "thumb_url": url.replace("w=1600", "w=800"),
                "full_url": url,
                "caption": f"{seed_hint} — View {i}",
            })
        return out

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

    # -----------------------------
    # CASE STUDIES payload
    # -----------------------------
    CASE_STUDIES = [
        {
            "title": "Tilal Al Ghaf",
            "hero_image_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=1600&auto=format&fit=crop",
            "summary": "Private courtyard pool framed by elegant cactus and olive trees with warm evening lighting.",
            "description": """A modern oasis in the heart of the city, featuring a private courtyard pool, sculptural cactus arrangements, and mature olive trees. Subtle lighting highlights natural textures for relaxed evenings and intimate gatherings.""",
            "completion_date": date(2025, 6, 27),
            "scope": "Design + Build + Pool",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Pool, Lighting, Courtyard",
            "is_featured": True,
            "sort_order": 1,
            "cta_url": "",
            "location": "Dubai, UAE",
            "project_type": "landscape",
            "gallery": five_dummy_images("Tilal Al Ghaf"),
        },
        {
            "title": "Murooj Al Furjan",
            "hero_image_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=1600&auto=format&fit=crop",
            "summary": "Luxury landscape with modern pool, pergola, and lush greenery for stylish outdoor living.",
            "description": """A contemporary outdoor program with a linear pool, shade pergola, and layered greenery. Optimized circulation for entertaining and low-maintenance planting tuned to Dubai’s climate.""",
            "completion_date": date(2025, 9, 3),
            "scope": "Design + Build",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Pergola, Pool",
            "is_featured": False,
            "sort_order": 2,
            "cta_url": "",
            "location": "Dubai, UAE",
            "project_type": "landscape",
            "gallery": five_dummy_images("Murooj Al Furjan"),
        },
        {
            "title": "Dubai Hills — Parkways (Minimalist Pool)",
            "hero_image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=2000&q=80",
            "thumb_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
            "full_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80",
            "summary": "Sleek pool, refined greenery, and architectural lines for calm, contemporary outdoor living.",
            "description": """A minimalist outdoor space with crisp water geometry, architectural planting, and considered hardscape. Visual quiet supports relaxation and everyday usability.""",
            "completion_date": date(2025, 7, 21),
            "scope": "Design + Build",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Minimalist, Pool",
            "is_featured": False,
            "sort_order": 3,
            "cta_url": "",
            "location": "Dubai, UAE",
            "project_type": "landscape",
            "gallery": five_dummy_images("Dubai Hills — Parkways"),
        },
        {
            "title": "Dubai Hills — Modern Villa Pool",
            "hero_image_url": "https://images.unsplash.com/photo-1523419409543-8a26d050f3c9?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1523419409543-8a26d050f3c9?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1523419409543-8a26d050f3c9?q=80&w=1600&auto=format&fit=crop",
            "summary": "Clean-lined pool with glass fencing and elegant, functional landscaping.",
            "description": """Balances safety and aesthetics with glass fencing, low-glare lighting, and drought-aware planting. Zones circulation for families and entertaining.""",
            "completion_date": date(2025, 9, 4),
            "scope": "Design + Build + Pool",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Pool, Family-friendly",
            "is_featured": False,
            "sort_order": 4,
            "cta_url": "",
            "location": "Dubai, UAE",
            "project_type": "landscape",
            "gallery": five_dummy_images("Dubai Hills — Modern Villa Pool"),
        },
        {
            "title": "Emirate Hills",
            "hero_image_url": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?q=80&w=1600&auto=format&fit=crop",
            "summary": "Resort-style landscape with palm-lined paths, reflective water, and soft evening lighting.",
            "description": """An elegant fusion of architecture and landscape. Manicured lawns, reflective pools, and palm allées create a resort ambiance with screened privacy.""",
            "completion_date": date(2025, 6, 29),
            "scope": "Design + Build",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Resort, Water Feature",
            "is_featured": True,
            "sort_order": 5,
            "cta_url": "",
            "location": "Dubai, UAE",
            "project_type": "landscape",
            "gallery": five_dummy_images("Emirate Hills"),
        },
        {
            "title": "Jumeirah Bay Rooftop",
            "hero_image_url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=2000&auto=format&fit=crop",
            "thumb_url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=800&auto=format&fit=crop",
            "full_url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=1600&auto=format&fit=crop",
            "summary": "Future-forward rooftop with panoramic views, comfort, and refined materials.",
            "description": """A high-performance rooftop terrace combining wind-conscious planting, integrated seating, and lighting tuned for skyline views.""",
            "completion_date": date(2025, 9, 4),
            "scope": "Design + Build",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Rooftop, Lighting",
            "is_featured": False,
            "sort_order": 6,
            "cta_url": "",
            "location": "Dubai, UAE",
            "project_type": "landscape",
            "gallery": five_dummy_images("Jumeirah Bay Rooftop"),
        },
    ]

    # -----------------------------
    # Locate target Service
    # -----------------------------
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
        svc = Service.objects.order_by("id").first()
        if not svc:
            print("[!] No Service records exist. Create one first.")
            sys.exit(1)

    print(f"[i] Seeding Case Studies for Service: {getattr(svc, 'title', svc.id)}")

    # -----------------------------
    # Do the work
    # -----------------------------
    with transaction.atomic():
        if args.wipe:
            print("[!] Wiping existing related rows…")
            svc.capabilities.all().delete()
            svc.process_steps.all().delete()
            svc.metrics.all().delete()
            svc.case_studies.all().delete()   # switched from project_images
            svc.editorial_images.all().delete()
            svc.partner_brands.all().delete()
            svc.testimonials.all().delete()
            svc.faqs.all().delete()
            svc.features.all().delete()
            svc.insights.all().delete()

        # Seed Case Studies
        for i, cs in enumerate(CASE_STUDIES, start=1):
            obj, _ = CaseStudy.objects.get_or_create(service=svc, title=cs["title"])
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
                    "cta_url": cs["cta_url"],
                    # Optional fields if present on your model:
                    "location": cs.get("location", ""),
                    "project_type": cs.get("project_type", ""),
                },
                [
                    "hero_image_url","thumb_url","full_url","summary","description",
                    "completion_date","scope","size_label","timeline_label","status_label",
                    "tags_csv","is_featured","sort_order","cta_url",
                    "location","project_type",
                ],
            )
            print(f" {'[~] Updated' if changed else '[=] Kept  '} Case Study • {obj.title}")

            # Optional gallery
            if HAS_CS_IMAGE and cs.get("gallery"):
                # Clear old images for this case study
                if hasattr(obj, "images"):
                    obj.images.all().delete()
                for g_i, img in enumerate(cs["gallery"], start=1):
                    CaseStudyImage.objects.create(
                        case_study=obj,
                        thumb_url=img["thumb_url"],
                        full_url=img["full_url"],
                        caption=img["caption"],
                        sort_order=g_i,
                    )
                print(f"     ↳ Seeded {len(cs['gallery'])} gallery images")
            elif not HAS_CS_IMAGE and cs.get("gallery"):
                print("     (Gallery provided but no CaseStudyImage model detected—skipping safely.)")

    print("[✓] Done seeding Case Studies.")

if __name__ == "__main__":
    main()
