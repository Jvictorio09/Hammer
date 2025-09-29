#!/usr/bin/env python3
"""
Seed a complete 'Interior Design & Build' Service page with rich, production-level content.

Usage:
  python seed_interiors.py --settings myProject.settings
  python seed_interiors.py --settings myProject.settings --wipe
  python seed_interiors.py --settings myProject.settings --title "Interior Design & Build" --slug "interior-design-build"

Notes:
- Idempotent: existing rows are updated in place (unless --wipe is used).
- Content includes hero, metrics, capabilities, process steps, editorial pairs (for BA), projects, FAQs, brands, testimonials, and insights.
"""

import os
import sys
import argparse
from pathlib import Path

# -----------------------------------------------------------------------------
# Django bootstrap
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Seed Interior Service + related content")
parser.add_argument("--settings", help="Django settings module (e.g. myProject.settings)")
parser.add_argument("--title", default="Interior Design & Build")
parser.add_argument("--slug", default="interior-design-build")
parser.add_argument("--wipe", action="store_true", help="Delete existing related rows before seeding")
args = parser.parse_args()

if args.settings:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)
elif not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django  # noqa: E402
django.setup()

from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from myApp.models import (  # noqa: E402
    Service,
    ServiceFeature,
    ServiceEditorialImage,
    ServiceProjectImage,
    ServiceCapability,
    ServiceProcessStep,
    ServiceMetric,
    ServiceFAQ,
    ServicePartnerBrand,
    ServiceTestimonial,
    Insight,
)

# -----------------------------------------------------------------------------
# Content (production-leaning)
# -----------------------------------------------------------------------------

HERO_MEDIA = "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=2000&auto=format&fit=crop"

SERVICE_DEFAULTS = dict(
    eyebrow="Interior",
    hero_headline="Premium Interior Design & Build in Dubai",
    hero_subcopy=(
        "Transforming spaces into timeless interiors with innovative design, "
        "premium materials, and meticulous craftsmanship—end-to-end by one accountable team."
    ),
    hero_media_url=HERO_MEDIA,
    pinned_heading="Our Capability",
    pinned_title="Timeless interiors, delivered with certainty.",
    pinned_body_1=(
        "From concept to completion, we curate materials, engineer details and manage fit-out to the highest standard. "
        "Every junction resolved. Every surface considered."
    ),
    pinned_body_2="Dedicated designers and engineers, a single contract, and a transparent weekly cadence.",
    insights_heading="Insights",
    insights_subcopy="Ideas, guides, and updates from our interior team.",
    stat_projects="350+",
    stat_years="20+ yrs",
    stat_specialists="In-house team",
    seo_meta_title="Premium Interior Design & Build in Dubai | Hammer Group",
    seo_meta_description=(
        "Design-to-build interiors for villas and commercial spaces in Dubai—concept, drawings, fit-out, "
        "joinery and styling—with fixed milestones and one integrated team."
    ),
    canonical_path="/services/interior-design-build/",
)

CAPABILITIES = [
    {
        "title": "Design Studio",
        "blurb": "Concept development, mood, space planning and FF&E curation.",
        "icon_class": "fa-solid fa-pen-ruler",
    },
    {
        "title": "2D / 3D & Drawings",
        "blurb": "Plans, elevations, details and 3D visualization ready for build.",
        "icon_class": "fa-solid fa-cube",
    },
    {
        "title": "Fit-Out & Site Works",
        "blurb": "Clean execution with tight protection, sequencing and QA.",
        "icon_class": "fa-solid fa-helmet-safety",
    },
    {
        "title": "Project Management",
        "blurb": "Fixed milestones, weekly reporting and stakeholder coordination.",
        "icon_class": "fa-solid fa-diagram-project",
    },
    {
        "title": "Engineering",
        "blurb": "MEP, acoustics and structural coordination resolved before site.",
        "icon_class": "fa-solid fa-gears",
    },
    {
        "title": "In-house Joinery",
        "blurb": "Custom kitchens, wardrobes and feature walls with premium finishes.",
        "icon_class": "fa-solid fa-screwdriver-wrench",
    },
    {
        "title": "Furniture & Lighting",
        "blurb": "FF&E specification, custom pieces and layered lighting scenes.",
        "icon_class": "fa-solid fa-lightbulb",
    },
    {
        "title": "Materials & Textures",
        "blurb": "Stone, timber and textiles selected to age beautifully in UAE climate.",
        "icon_class": "fa-solid fa-layer-group",
    },
]

PROCESS = [
    {"step_no": 1, "title": "Discovery & Brief",        "description": "Lifestyle, brand and budget alignment with site study."},
    {"step_no": 2, "title": "Concept & 3D",             "description": "Mood, space planning and photoreal views for sign-off."},
    {"step_no": 3, "title": "Technical & BOQ",          "description": "Detailed drawings, MEP integration, schedules and cost book."},
    {"step_no": 4, "title": "Procurement & Joinery",    "description": "Long-lead items secured; custom joinery manufactured."},
    {"step_no": 5, "title": "Fit-Out & Commissioning",  "description": "Sequenced works, QA, snag-free finishes and systems testing."},
    {"step_no": 6, "title": "Styling & Handover",       "description": "FF&E placement, lighting scenes and documentation for care."},
]

METRICS = [
    {"value": "350+",   "label": "Interiors Delivered"},
    {"value": "20+ yrs","label": "Operating in Dubai"},
    {"value": "98%",    "label": "On-time Handover"},
]

# Even count for BA pairs (2 pairs here)
EDITORIALS = [
    {"image_url": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop", "caption": "Living Room — Before"},
    {"image_url": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?q=80&w=1600&auto=format&fit=crop", "caption": "Living Room — After"},
    {"image_url": "https://images.unsplash.com/photo-1505691723518-36a5ac3b2b8f?q=80&w=1600&auto=format&fit=crop", "caption": "Kitchen — Before"},
    {"image_url": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?q=80&w=1600&auto=format&fit=crop", "caption": "Kitchen — After"},
]

# 5 works best for A/B/C/D/E desktop layout
PROJECTS = [
    {
        "thumb_url": "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Minimalist living, Palm Jumeirah",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1484101403633-562f891dc89a?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1484101403633-562f891dc89a?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Sculpted kitchen & joinery",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1505692794403-34d4982f88aa?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1505692794403-34d4982f88aa?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Warm textures & stone",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Executive workspace",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Statement bedroom suite",
    },
]

BRANDS = [
    {"name": "Cosentino",      "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Cosentino",     "site_url": "https://www.cosentino.com/"},
    {"name": "Flos",           "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Flos",          "site_url": "https://www.flos.com/"},
    {"name": "Herman Miller",  "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Herman+Miller", "site_url": "https://www.hermanmiller.com/"},
]

TESTIMONIALS = [
    {
        "author": "A. Rahman",
        "role_company": "Villa Owner, Dubai Hills",
        "quote": "Hammer turned ideas into a home that feels effortless. On schedule, zero surprises.",
        "headshot_url": "https://i.pravatar.cc/120?img=15",
    },
    {
        "author": "N. Haddad",
        "role_company": "GM, Boutique Hospitality",
        "quote": "Detail-obsessed team. Joinery and finishes were immaculate—guests noticed day one.",
        "headshot_url": "https://i.pravatar.cc/120?img=28",
    },
]

FAQS = [
    {
        "question": "How soon can you start?",
        "answer": "Typically 2–4 weeks from concept sign-off. Long-lead materials are flagged early to protect timelines.",
    },
    {
        "question": "Can you work while the space is occupied?",
        "answer": "Yes. We plan phased works, dust control and protection to keep life and business moving.",
    },
    {
        "question": "Do you handle approvals and MEP?",
        "answer": "Yes. Our engineering team coordinates MEP and manages authority submissions end-to-end.",
    },
    {
        "question": "What about custom joinery lead times?",
        "answer": "Most custom pieces take 3–8 weeks depending on finishes. We sequence procurement to stay on track.",
    },
    {
        "question": "Do you provide aftercare?",
        "answer": "We offer post-handover support for touch-ups, seasonal adjustments and minor tweaks.",
    },
]

# Feature chips for overview fallbacks
FEATURES_FOR_FALLBACK = [
    {"icon_class": "fa-solid fa-pen-ruler",     "label": "Concept & Space Planning"},
    {"icon_class": "fa-solid fa-cube",          "label": "2D / 3D Visualization"},
    {"icon_class": "fa-solid fa-helmet-safety", "label": "Fit-Out"},
    {"icon_class": "fa-solid fa-diagram-project","label": "Project Management"},
    {"icon_class": "fa-solid fa-gears",         "label": "Engineering"},
    {"icon_class": "fa-solid fa-screwdriver-wrench","label": "Custom Joinery"},
    {"icon_class": "fa-solid fa-lightbulb",     "label": "Furniture & Lighting"},
    {"icon_class": "fa-solid fa-layer-group",   "label": "Materials & Textures"},
]

INSIGHTS = [
    {
        "title": "Material palettes that age well in Dubai",
        "cover_image_url": "https://picsum.photos/1200/700?random=92001",
        "tag": "Materials",
        "excerpt": "How to combine stone, timber and textiles for long-life interiors in UAE climate.",
        "read_minutes": 5,
        "body": "Choosing dense stones, engineered timbers and performance textiles reduces maintenance while keeping the tactile richness clients expect…",
    },
    {
        "title": "Lighting layers for calm interiors",
        "cover_image_url": "https://picsum.photos/1200/700?random=92002",
        "tag": "Lighting",
        "excerpt": "Ambient, task and accent—the simple framework behind relaxing rooms.",
        "read_minutes": 4,
        "body": "Start with warm ambient light, add task where needed, then punctuate with accents. Keep glare low and dimming curves smooth for evening comfort…",
    },
]

# -----------------------------------------------------------------------------
# Helpers (upsert-style)
# -----------------------------------------------------------------------------

def upsert(instance, data: dict, fields: list[str]) -> bool:
    """Update instance fields from data. Return True if any field changed."""
    changed = False
    for f in fields:
        new = data.get(f)
        if new is not None and getattr(instance, f) != new:
            setattr(instance, f, new)
            changed = True
    if changed:
        instance.save()
    return changed

# -----------------------------------------------------------------------------
# Seeder
# -----------------------------------------------------------------------------

@transaction.atomic
def seed(title: str, slug: str, wipe: bool = False):
    svc, created = Service.objects.get_or_create(
        slug=slug,
        defaults={"title": title, **SERVICE_DEFAULTS},
    )
    if not created:
        changed = upsert(
            svc,
            {"title": title, **SERVICE_DEFAULTS},
            [
                "title",
                "eyebrow",
                "hero_headline",
                "hero_subcopy",
                "hero_media_url",
                "pinned_heading",
                "pinned_title",
                "pinned_body_1",
                "pinned_body_2",
                "insights_heading",
                "insights_subcopy",
                "stat_projects",
                "stat_years",
                "stat_specialists",
                "seo_meta_title",
                "seo_meta_description",
                "canonical_path",
            ],
        )
        print(f"[i] Service exists: {svc.title} ({'updated' if changed else 'no change'})")
    else:
        print(f"[+] Created service: {svc.title}")

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

    # Capabilities
    for i, c in enumerate(CAPABILITIES, start=1):
        obj, _ = ServiceCapability.objects.get_or_create(service=svc, title=c["title"])
        changed = upsert(obj, {**c, "sort_order": i}, ["blurb", "icon_class", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Capability • {obj.title}")

    # Process steps
    for i, s in enumerate(PROCESS, start=1):
        obj, _ = ServiceProcessStep.objects.get_or_create(service=svc, step_no=s["step_no"], title=s["title"])
        changed = upsert(obj, {**s, "sort_order": i}, ["description", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Step {obj.step_no:02d} • {obj.title}")

    # Metrics
    for i, m in enumerate(METRICS, start=1):
        obj, _ = ServiceMetric.objects.get_or_create(service=svc, label=m["label"])
        changed = upsert(obj, {"value": m["value"], "sort_order": i}, ["value", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Metric • {obj.value} {obj.label}")

    # Projects
    for i, p in enumerate(PROJECTS, start=1):
        obj, _ = ServiceProjectImage.objects.get_or_create(service=svc, full_url=p["full_url"])
        changed = upsert(obj, {**p, "sort_order": i}, ["thumb_url", "caption", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Project • {obj.caption or obj.full_url}")

    # Editorials (for BA)
    for i, e in enumerate(EDITORIALS, start=1):
        obj, _ = ServiceEditorialImage.objects.get_or_create(service=svc, image_url=e["image_url"])
        changed = upsert(obj, {**e, "sort_order": i}, ["caption", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Editorial • {obj.caption or obj.image_url}")

    # Brands
    for i, b in enumerate(BRANDS, start=1):
        obj, _ = ServicePartnerBrand.objects.get_or_create(service=svc, name=b["name"])
        changed = upsert(obj, {**b, "sort_order": i}, ["logo_url", "site_url", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Brand • {obj.name}")

    # Testimonials
    for i, t in enumerate(TESTIMONIALS, start=1):
        obj, _ = ServiceTestimonial.objects.get_or_create(service=svc, author=t["author"], quote=t["quote"])
        changed = upsert(obj, {**t, "sort_order": i}, ["role_company", "headshot_url", "sort_order"])
        who = f"{obj.author} ({obj.role_company})" if obj.role_company else obj.author
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Testimonial • {who}")

    # FAQs
    for i, q in enumerate(FAQS, start=1):
        obj, _ = ServiceFAQ.objects.get_or_create(service=svc, question=q["question"])
        changed = upsert(obj, {"answer": q.get("answer", ""), "sort_order": i}, ["answer", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} FAQ • {obj.question[:60]}")

    # Fallback features (ensure Overview chips render even if capabilities hidden)
    for i, f in enumerate(FEATURES_FOR_FALLBACK, start=1):
        obj, _ = ServiceFeature.objects.get_or_create(service=svc, label=f["label"])
        changed = upsert(obj, {**f, "sort_order": i}, ["icon_class", "sort_order"])
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Feature • {obj.label}")

    # Insights
    for i, item in enumerate(INSIGHTS, start=1):
        obj, _ = Insight.objects.get_or_create(service=svc, title=item["title"])
        payload = {
            "cover_image_url": item.get("cover_image_url", ""),
            "tag": item.get("tag", ""),
            "excerpt": item.get("excerpt", ""),
            "body": item.get("body", ""),
            "read_minutes": item.get("read_minutes", 4),
            "published": True,
            "published_at": obj.published_at or timezone.now(),
        }
        changed = upsert(
            obj,
            payload,
            ["cover_image_url", "tag", "excerpt", "body", "read_minutes", "published", "published_at"],
        )
        print(f" {'[~] Updated' if changed else '[=] Kept  '} Insight • {obj.title}")

    return svc

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    svc = seed(args.title, args.slug, wipe=args.wipe)
    print("\n✔ Seed complete.")
    print(f"→ Visit {svc.canonical_path or f'/services/{svc.slug}/'}")
    print("Tip: Add editorial images in even counts so the Before/After panel renders clean pairs.")
    print("Tip: Use transparent PNG/SVG brand logos for the cleanest row.")
