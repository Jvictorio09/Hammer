#!/usr/bin/env python3
"""
Seed a complete 'Joinery' Service page with rich, production-level content.

Usage:
  python seed_joinery.py --settings myProject.settings
  python seed_joinery.py --settings myProject.settings --wipe
  python seed_joinery.py --settings myProject.settings --title "Joinery" --slug "joinery"

Notes:
- Idempotent: existing rows are updated (unless --wipe).
- Mirrors your service model: hero, metrics, capabilities, steps, editorial pairs (for BA), projects, FAQs, brands, testimonials, insights.
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

parser = argparse.ArgumentParser(description="Seed Joinery Service + related content")
parser.add_argument("--settings", help="Django settings module (e.g. myProject.settings)")
parser.add_argument("--title", default="Joinery")
parser.add_argument("--slug", default="joinery")
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
# Content
# -----------------------------------------------------------------------------

HERO_MEDIA = "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=2000&auto=format&fit=crop"

SERVICE_DEFAULTS = dict(
    eyebrow="Joinery",
    hero_headline="Premium Bespoke Joinery in Dubai",
    hero_subcopy=(
        "Equipped with a 22,000 sqft production house, our joinery division delivers bespoke kitchens, "
        "wardrobes, feature walls and furniture with in-house experts, advanced CNC, and rigorous QA—"
        "from drawings to install by one accountable team."
    ),
    hero_media_url=HERO_MEDIA,
    pinned_heading="Our Capability",
    pinned_title="Precision joinery, crafted for daily life.",
    pinned_body_1=(
        "From design intent and shop drawings to sampling, production and site install, "
        "we control every detail in-house. Tight tolerances, clean sequencing, and finishes "
        "that perform in UAE climate."
    ),
    pinned_body_2="Dedicated engineers and installers, a single contract, and a transparent weekly cadence.",
    insights_heading="Insights",
    insights_subcopy="Materials, hardware and finishing know-how from the workshop floor.",
    stat_projects="300+",
    stat_years="20+ yrs",
    stat_specialists="60+",
    seo_meta_title="Bespoke Joinery in Dubai | Hammer Group",
    seo_meta_description=(
        "Premium custom joinery for villas and commercial spaces in Dubai—kitchens, wardrobes, "
        "feature walls and furniture—engineered, produced and installed by one integrated team."
    ),
    canonical_path="/services/joinery/",
)

CAPABILITIES = [
    {
        "title": "Kitchens & Wardrobes",
        "blurb": "Custom layouts, carcasses and fronts with premium hardware and integrated lighting.",
        "icon_class": "fa-solid fa-kitchen-set",  # Font Awesome 6 Pro icon; fall back if your kit lacks it
    },
    {
        "title": "Bespoke Furniture",
        "blurb": "Tables, consoles and built-ins that balance craft with durability.",
        "icon_class": "fa-solid fa-couch",
    },
    {
        "title": "Doors & Wall Paneling",
        "blurb": "Acoustic and decorative systems with hidden access and flush detailing.",
        "icon_class": "fa-solid fa-door-closed",
    },
    {
        "title": "Feature Walls & Receptions",
        "blurb": "Statement pieces combining timber, metal, stone and lighting.",
        "icon_class": "fa-solid fa-landmark",
    },
    {
        "title": "In-house Joinery Workshop",
        "blurb": "22,000 sqft with CNC, edge-banding, pressing and controlled finishing.",
        "icon_class": "fa-solid fa-industry",
    },
    {
        "title": "Engineering & Shop Drawings",
        "blurb": "MEP coordination, tolerances and fixing details resolved before cut.",
        "icon_class": "fa-solid fa-gears",
    },
    {
        "title": "Finishes & Textures",
        "blurb": "Lacquer, veneer, thermofoil, HPL, FENIX, laminam—sampled and signed-off.",
        "icon_class": "fa-solid fa-layer-group",
    },
    {
        "title": "Site Install Team",
        "blurb": "Dust control, protection and clean sequencing for live environments.",
        "icon_class": "fa-solid fa-helmet-safety",
    },
]

PROCESS = [
    {"step_no": 1, "title": "Discovery & Survey",       "description": "Use, storage and services mapped on site; constraints and tolerances set."},
    {"step_no": 2, "title": "Design Intent & Drawings", "description": "Shop drawings, sections and hardware schedules coordinated with MEP."},
    {"step_no": 3, "title": "Samples & Mock-ups",       "description": "Finish boards and key junction mock-ups for sign-off."},
    {"step_no": 4, "title": "CNC & Production",         "description": "Cutting, edging and pressing with QA at each station."},
    {"step_no": 5, "title": "Assembly & Finishing",     "description": "Dry fit, hardware, lighting channels; lacquer/veneer finishing."},
    {"step_no": 6, "title": "Install & Handover",       "description": "Sequenced delivery, protection, final alignment and documentation."},
]

METRICS = [
    {"value": "22,000 sqft", "label": "Production Facility"},
    {"value": "±1 mm",       "label": "Typical Tolerance"},
    {"value": "98%",         "label": "On-time Handover"},
]

# Even count → used as BA pairs (e.g., 2 pairs)
EDITORIALS = [
    # Wardrobe
    {"image_url": "https://images.unsplash.com/photo-1505691723518-36a5ac3b2b8f?q=80&w=1600&auto=format&fit=crop", "caption": "Wardrobe — Before"},
    {"image_url": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?q=80&w=1600&auto=format&fit=crop", "caption": "Wardrobe — After"},
    # Kitchen
    {"image_url": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop", "caption": "Kitchen — Before"},
    {"image_url": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?q=80&w=1600&auto=format&fit=crop", "caption": "Kitchen — After"},
]

PROJECTS = [
    {
        "thumb_url": "https://images.unsplash.com/photo-1484101403633-562f891dc89a?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1484101403633-562f891dc89a?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Sculpted kitchen with integrated lighting",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Minimalist living cabinetry, Palm Jumeirah",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Executive wall system with acoustic doors",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1505692794403-34d4982f88aa?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1505692794403-34d4982f88aa?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Warm veneer & stone feature reception",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Statement bedroom suite with concealed storage",
    },
]

BRANDS = [
    {"name": "Blum",          "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Blum",          "site_url": "https://www.blum.com/"},
    {"name": "Hettich",       "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Hettich",       "site_url": "https://web.hettich.com/"},
    {"name": "FENIX",         "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=FENIX",         "site_url": "https://www.fenixforinteriors.com/"},
    {"name": "Egger",         "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Egger",         "site_url": "https://www.egger.com/"},
    {"name": "Cosentino",     "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Cosentino",     "site_url": "https://www.cosentino.com/"},
]

TESTIMONIALS = [
    {
        "author": "A. Rahman",
        "role_company": "Villa Owner, Dubai Hills",
        "quote": "Our kitchen and wardrobes feel tailor-made to how we live. The site team was tidy and on time.",
        "headshot_url": "https://i.pravatar.cc/120?img=15",
    },
    {
        "author": "N. Haddad",
        "role_company": "GM, Boutique Hospitality",
        "quote": "Detail-obsessed workshop. Edges, reveals, finishes—all immaculate. Handover was snag-free.",
        "headshot_url": "https://i.pravatar.cc/120?img=28",
    },
]

FAQS = [
    {
        "question": "How long does production usually take?",
        "answer": "Typical lead times range from 3–8 weeks depending on scope and finishes. Long-lead items are flagged early to protect the schedule.",
    },
    {
        "question": "Can you match existing finishes or veneers?",
        "answer": "Yes. We provide finish boards and can book-match veneers. We’ll propose the closest options and mock up key junctions.",
    },
    {
        "question": "Which hardware systems do you use?",
        "answer": "We specify premium hardware (e.g., Blum/Hettich) with soft-close, tip-on, and pocket options. Alternatives can be proposed to suit budget.",
    },
    {
        "question": "Do you coordinate with MEP and appliances?",
        "answer": "Yes. Shop drawings and cut-outs are coordinated with MEP and appliance schedules before CNC to avoid rework on site.",
    },
    {
        "question": "Do you provide aftercare?",
        "answer": "We offer post-handover support for seasonal adjustments, minor touch-ups and care guidance for each finish.",
    },
]

# Small feature tokens you can surface in an Overview list if needed
FEATURES_FOR_FALLBACK = [
    {"icon_class": "fa-solid fa-cube",            "label": "CNC Precision"},
    {"icon_class": "fa-solid fa-layer-group",     "label": "Veneer & Lacquer"},
    {"icon_class": "fa-solid fa-screwdriver-wrench","label": "In-house Assembly"},
    {"icon_class": "fa-solid fa-truck-ramp-box",  "label": "Sequenced Install"},
]

INSIGHTS = [
    {
        "title": "Choosing hardware that lasts",
        "cover_image_url": "https://picsum.photos/1200/700?random=93001",
        "tag": "Hardware",
        "excerpt": "Slides, hinges and lift systems—what actually matters for daily use.",
        "read_minutes": 4,
        "body": "Focus on cycle ratings, adjustability and after-sales support. Good hardware maintains alignment and feel for years, not months…",
    },
    {
        "title": "Veneer matching 101",
        "cover_image_url": "https://picsum.photos/1200/700?random=93002",
        "tag": "Finishes",
        "excerpt": "How to specify grain direction, sequencing and edge reveals.",
        "read_minutes": 5,
        "body": "Agree early on crown vs quarter, continuous runs, and edge reveal sizes. Mock-ups prevent surprises on site and speed up sign-off…",
    },
]

# -----------------------------------------------------------------------------
# Helpers
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

    # Features (for any Overview chips)
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
