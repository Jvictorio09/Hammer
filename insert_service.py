#!/usr/bin/env python3
"""
Seed a premium Service page with related content.

Usage:
  python insert_service.py --settings yourproject.settings
  (or set DJANGO_SETTINGS_MODULE in env, then just `python insert_service.py`)

Options:
  --title "Landscape Design & Build"
  --slug "landscape-design-build"
  --wipe (delete existing related rows for this service before seeding)
"""

import os
import sys
import argparse
from pathlib import Path

# --- Django bootstrap ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Seed Service + related content")
parser.add_argument("--settings", help="Django settings module (e.g. yourproject.settings)")
parser.add_argument("--title", default="Landscape Design & Build")
parser.add_argument("--slug", default="landscape-design-build")
parser.add_argument("--wipe", action="store_true", help="Delete existing related rows before seeding")
args = parser.parse_args()

if args.settings:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)
elif not os.environ.get("DJANGO_SETTINGS_MODULE"):
    # Fallback: try a common name. EDIT if needed.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django  # noqa: E402
django.setup()

from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

# EDIT app label if your models live elsewhere:
from myApp.models import (  # noqa: E402
    Service, ServiceFeature, ServiceEditorialImage, ServiceProjectImage, Insight,
    ServiceCapability, ServiceProcessStep, ServiceMetric, ServiceFAQ,
    ServicePartnerBrand, ServiceTestimonial
)

# --- data ---------------------------------------------------------------------
HERO_MEDIA = "https://picsum.photos/1920/1080?random=90001"

CAPABILITIES = [
    {"title": "Native & Low-Water Planting", "blurb": "Drought-smart palettes and drip irrigation engineered for the UAE climate.", "icon_class": "fa-solid fa-seedling"},
    {"title": "Custom Pools & Water Features", "blurb": "Shotcrete shells, waterproofing, lighting, and automation—built to spec.", "icon_class": "fa-solid fa-water-ladder"},
    {"title": "Pergolas, Decks & Hardscape", "blurb": "Timber/metal pergolas, stone paving, outdoor kitchens and shaded rooms.", "icon_class": "fa-solid fa-umbrella-beach"},
]

PROCESS = [
    {"step_no": 1, "title": "Consult & Brief", "description": "Site walk, measurements, constraints, and budget alignment."},
    {"step_no": 2, "title": "Concept & 3D", "description": "2D planning, 3D visuals, and material boards for approval."},
    {"step_no": 3, "title": "Engineering & Permits", "description": "Technical drawings, MEP coordination, authority submissions."},
    {"step_no": 4, "title": "Build & Handover", "description": "Program, QA, commissioning, and aftercare onboarding."},
]

METRICS = [
    {"value": "650+", "label": "Projects Delivered"},
    {"value": "20+ yrs", "label": "Operating in Dubai"},
    {"value": "98%", "label": "On-time Handover"},
]

PROJECTS = [
    # thumbs (800x600), full (1600x1200)
    {"thumb_url": "https://picsum.photos/800/600?random=42001", "full_url": "https://picsum.photos/1600/1200?random=42001", "caption": "Courtyard pool with pergola"},
    {"thumb_url": "https://picsum.photos/800/600?random=42002", "full_url": "https://picsum.photos/1600/1200?random=42002", "caption": "Low-water garden & stonework"},
    {"thumb_url": "https://picsum.photos/800/600?random=42003", "full_url": "https://picsum.photos/1600/1200?random=42003", "caption": "Sculptural lighting & pathways"},
    {"thumb_url": "https://picsum.photos/800/600?random=42004", "full_url": "https://picsum.photos/1600/1200?random=42004", "caption": "Outdoor kitchen & deck"},
]

EDITORIALS = [
    {"image_url": "https://picsum.photos/1200/800?random=43001", "caption": "Evening ambience"},
    {"image_url": "https://picsum.photos/1200/800?random=43002", "caption": "Native & low-water"},
    {"image_url": "https://picsum.photos/1200/800?random=43003", "caption": "Outdoor rooms"},
]

BRANDS = [
    {"name": "Cosentino", "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Cosentino", "site_url": "https://www.cosentino.com/"},
    {"name": "Hunter Irrigation", "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Hunter", "site_url": "https://www.hunterindustries.com/"},
]

TESTIMONIALS = [
    {"author": "R. Al Mansoori", "role_company": "Private Villa Owner", "quote": "Hammer turned our yard into a resort. Clear schedule, zero surprises.", "headshot_url": "https://i.pravatar.cc/100?img=12"},
    {"author": "S. Haddad", "role_company": "Hospitality Director", "quote": "Their coordination between design and build saved us weeks.", "headshot_url": "https://i.pravatar.cc/100?img=22"},
]

FAQS = [
    {"question": "Do you handle permits and authority approvals?", "answer": "Yes. Our engineering team prepares drawings and manages submissions end-to-end."},
    {"question": "Can you work in phases to match our budget?", "answer": "Absolutely. We can stage scope—start with essential hardscape, add features later."},
    {"question": "Do you provide maintenance after handover?", "answer": "Yes. Our FM team offers aftercare packages for irrigation, lighting, and softscape."},
]

# Also seed a few basic features so the page can gracefully fall back when Capabilities are removed.
FALLBACK_FEATURES = [
    {"icon_class": "fa-solid fa-seedling", "label": "Native / Low-water"},
    {"icon_class": "fa-solid fa-water-ladder", "label": "Custom Pools"},
    {"icon_class": "fa-solid fa-umbrella-beach", "label": "Pergolas & Decks"},
]

INSIGHT = {
    "title": "Planning a drought-smart garden in Dubai",
    "cover_image_url": "https://picsum.photos/1200/700?random=91001",
    "tag": "Landscape",
    "excerpt": "Water-wise planting and efficient irrigation—without losing the lush look.",
    "read_minutes": 4,
}

# --- seeding ------------------------------------------------------------------
@transaction.atomic
def seed_service(title: str, slug: str, wipe: bool = False):
    svc, created = Service.objects.get_or_create(
        slug=slug,
        defaults=dict(
            title=title,
            eyebrow="Landscape",
            hero_headline="Quiet-Luxury Landscape Design & Build in Dubai",
            hero_subcopy=(
                "Native planting. Custom pools & pergolas. Architectural lighting. "
                "One integrated team—from concept to aftercare."
            ),
            hero_media_url=HERO_MEDIA,
            pinned_heading="Our Capability",
            pinned_title="Landscapes that live beautifully—day and night.",
            pinned_body_1="Outdoor rooms that feel effortless to use and maintain.",
            pinned_body_2="One integrated contract from concept to aftercare.",
            insights_heading="Insights",
            insights_subcopy="Ideas, guides, and updates from our team.",
            stat_projects="650+",
            stat_years="20+",
            stat_specialists="1000+",
            seo_meta_title=f"{title} | Hammer Group",
            seo_meta_description="Premium landscape design & build with clear milestones and one accountable team.",
            canonical_path=f"/services/{slug}/",
        ),
    )

    if not created:
        print(f"[i] Service exists: {svc.title} ({svc.slug})")
    else:
        print(f"[+] Created service: {svc.title} ({svc.slug})")

    if wipe:
        print("[!] Wiping existing related rows…")
        svc.capabilities.all().delete()
        svc.process_steps.all().delete()
        svc.metrics.all().delete()
        svc.project_images.all().delete()
        svc.editorial_images.all().delete()
        svc.partner_brands.all().delete()
        svc.testimonials.all().delete()
        svc.faqs.all().delete()
        svc.features.all().delete()
        svc.insights.all().delete()

    # Capabilities (3)
    for i, c in enumerate(CAPABILITIES, start=1):
        obj, was_new = ServiceCapability.objects.get_or_create(
            service=svc, title=c["title"],
            defaults=dict(blurb=c.get("blurb", ""), icon_class=c.get("icon_class", "fa-solid fa-circle-check"), sort_order=i)
        )
        print((" [+] Capability: " if was_new else " [i] Capability exists: ") + obj.title)

    # Process steps (4)
    for i, s in enumerate(PROCESS, start=1):
        obj, was_new = ServiceProcessStep.objects.get_or_create(
            service=svc, step_no=s["step_no"], title=s["title"],
            defaults=dict(description=s.get("description", ""), sort_order=i)
        )
        print((" [+] Step: " if was_new else " [i] Step exists: ") + f"{obj.step_no} • {obj.title}")

    # Metrics (3)
    for i, m in enumerate(METRICS, start=1):
        obj, was_new = ServiceMetric.objects.get_or_create(
            service=svc, label=m["label"],
            defaults=dict(value=m["value"], sort_order=i)
        )
        print((" [+] Metric: " if was_new else " [i] Metric exists: ") + f"{obj.value} {obj.label}")

    # Project images (4)
    for i, p in enumerate(PROJECTS, start=1):
        obj, was_new = ServiceProjectImage.objects.get_or_create(
            service=svc, full_url=p["full_url"],
            defaults=dict(thumb_url=p["thumb_url"], caption=p.get("caption", ""), sort_order=i)
        )
        print((" [+] Project image: " if was_new else " [i] Project image exists: ") + obj.caption)

    # Editorial images (3)
    for i, e in enumerate(EDITORIALS, start=1):
        obj, was_new = ServiceEditorialImage.objects.get_or_create(
            service=svc, image_url=e["image_url"],
            defaults=dict(caption=e.get("caption", ""), sort_order=i)
        )
        print((" [+] Editorial: " if was_new else " [i] Editorial exists: ") + obj.caption)

    # Partner brands (2)
    for i, b in enumerate(BRANDS, start=1):
        obj, was_new = ServicePartnerBrand.objects.get_or_create(
            service=svc, name=b["name"],
            defaults=dict(logo_url=b.get("logo_url", ""), site_url=b.get("site_url", ""), sort_order=i)
        )
        print((" [+] Brand: " if was_new else " [i] Brand exists: ") + obj.name)

    # Testimonials (2)
    for i, t in enumerate(TESTIMONIALS, start=1):
        obj, was_new = ServiceTestimonial.objects.get_or_create(
            service=svc, author=t["author"], quote=t["quote"],
            defaults=dict(role_company=t.get("role_company", ""), headshot_url=t.get("headshot_url", ""), sort_order=i)
        )
        who = f"{obj.author} ({obj.role_company})" if obj.role_company else obj.author
        print((" [+] Testimonial: " if was_new else " [i] Testimonial exists: ") + who)

    # FAQs (3)
    for i, q in enumerate(FAQS, start=1):
        obj, was_new = ServiceFAQ.objects.get_or_create(
            service=svc, question=q["question"],
            defaults=dict(answer=q.get("answer", ""), sort_order=i)
        )
        print((" [+] FAQ: " if was_new else " [i] FAQ exists: ") + obj.question)

    # Fallback basic features (for empty-state test)
    for i, f in enumerate(FALLBACK_FEATURES, start=1):
        obj, was_new = ServiceFeature.objects.get_or_create(
            service=svc, label=f["label"],
            defaults=dict(icon_class=f.get("icon_class", "fa-solid fa-circle-check"), sort_order=i)
        )
        print((" [+] Feature: " if was_new else " [i] Feature exists: ") + obj.label)

    # One insight (optional)
    ins, new_ins = Insight.objects.get_or_create(
        service=svc, title=INSIGHT["title"],
        defaults=dict(
            cover_image_url=INSIGHT["cover_image_url"],
            tag=INSIGHT["tag"], excerpt=INSIGHT["excerpt"],
            body="…", read_minutes=INSIGHT["read_minutes"],
            published=True, published_at=timezone.now(),
        )
    )
    print((" [+] Insight: " if new_ins else " [i] Insight exists: ") + ins.title)

    return svc


if __name__ == "__main__":
    svc = seed_service(args.title, args.slug, wipe=args.wipe)
    path = svc.canonical_path or f"/services/{svc.slug}/"
    print("\n✔ Seed complete.")
    print(f"→ Visit {path}")
    print("Tip: For empty-state test, delete Capabilities in admin; the page will fall back to Features or hide the grid.")
    print("Tip: Set SEO fields on the Service to see <title>, meta description, and JSON-LD change.")
