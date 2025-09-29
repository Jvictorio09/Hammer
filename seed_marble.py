#!/usr/bin/env python3
"""
Seed a complete 'Marble' Service page with rich, production-level content.

Usage:
  python seed_marble.py --settings myProject.settings
  python seed_marble.py --settings myProject.settings --wipe
  python seed_marble.py --settings myProject.settings --title "Marble" --slug "marble"

Notes:
- Idempotent: existing rows are updated (unless --wipe).
- Populates hero, metrics, capabilities, steps, editorial pairs (for Before/After),
  projects, FAQs, brands, testimonials, and insights.
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

parser = argparse.ArgumentParser(description="Seed Marble Service + related content")
parser.add_argument("--settings", help="Django settings module (e.g. myProject.settings)")
parser.add_argument("--title", default="Marble")
parser.add_argument("--slug", default="marble")
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

HERO_MEDIA = "https://images.unsplash.com/photo-1523419409543-8b8d5a5f7f86?q=80&w=2000&auto=format&fit=crop"

SERVICE_DEFAULTS = dict(
    eyebrow="Marble",
    hero_headline="Custom Marble Fabrication & Installation in Dubai",
    hero_subcopy=(
        "Hammer designs, fabricates and installs elevated marble fixtures and fittings—interior and exterior—"
        "using best-in-class materials, precision templating and in-house production for book-matched slabs, "
        "feature cladding and statement surfaces."
    ),
    hero_media_url=HERO_MEDIA,
    pinned_heading="Our Capability",
    pinned_title="Stone, engineered to live beautifully.",
    pinned_body_1=(
        "From slab selection and book-match layouts to CNC/water-jet cutting, dry-lay and sealed installation, "
        "we manage the entire stone workflow in-house. Tolerances are tight, junctions are resolved, and logistics "
        "are sequenced for clean, on-time delivery."
    ),
    pinned_body_2="One accountable team. Transparent weekly cadence. Finishes that last in UAE climate.",
    insights_heading="Insights",
    insights_subcopy="Guides on stone selection, sealing and detailing for Dubai environments.",
    stat_projects="250+",
    stat_years="20+ yrs",
    stat_specialists="40+",
    seo_meta_title="Custom Marble Fabrication & Installation in Dubai | Hammer Group",
    seo_meta_description=(
        "Premium marble for interiors and exteriors in Dubai—vanities, kitchens, staircases, reception desks "
        "and facade cladding—book-matched, CNC cut and expertly installed by one integrated team."
    ),
    canonical_path="/services/marble/",
)

CAPABILITIES = [
    {
        "title": "Slab Curation & Procurement",
        "blurb": "Sourcing premium marble, quartzite and porcelain slabs; grading and yield planning.",
        "icon_class": "fa-solid fa-gem",
    },
    {
        "title": "Book-matching & Vein Mapping",
        "blurb": "Mirror and end-match layouts with digital overlays before cutting.",
        "icon_class": "fa-solid fa-shapes",
    },
    {
        "title": "CNC / Water-jet Cutting",
        "blurb": "Precision cut-outs, miters and inlays with ±1 mm tolerances.",
        "icon_class": "fa-solid fa-ruler-combined",
    },
    {
        "title": "Countertops & Vanities",
        "blurb": "Mitred edges, integrated sinks, shadow-gaps and discreet joints.",
        "icon_class": "fa-solid fa-layer-group",
    },
    {
        "title": "Staircases & Feature Cladding",
        "blurb": "Treads, risers, stringers and large-format walls with hidden fixings.",
        "icon_class": "fa-solid fa-border-all",
    },
    {
        "title": "Finishing & Protection",
        "blurb": "Honing/polish, edge detailing, sealing systems and aftercare guides.",
        "icon_class": "fa-solid fa-shield-halved",
    },
    {
        "title": "Site Installation",
        "blurb": "Dry-lay QA, protection and clean sequencing for live interiors and exteriors.",
        "icon_class": "fa-solid fa-helmet-safety",
    },
]

PROCESS = [
    {"step_no": 1, "title": "Survey & Templating",            "description": "Laser survey and templates; tolerances and joints defined early."},
    {"step_no": 2, "title": "Slab Selection & Book-match",    "description": "Vein mapping and mock layouts for client sign-off."},
    {"step_no": 3, "title": "Shop Drawings & Dry-lay",        "description": "Details, edge profiles and junctions resolved; dry-lay QA photos."},
    {"step_no": 4, "title": "CNC / Water-jet Cutting",        "description": "Precision cutting, rebates, miters and sink/hob cut-outs."},
    {"step_no": 5, "title": "Finishing & QC",                 "description": "Hone/polish, edge treatment, sealing tests and labeling."},
    {"step_no": 6, "title": "Install & Sealing",              "description": "Sequenced install, protection, final alignment and handover care guide."},
]

METRICS = [
    {"value": "±1 mm",        "label": "Typical Tolerance"},
    {"value": "250+",         "label": "Stone Projects"},
    {"value": "98%",          "label": "On-time Handover"},
]

# Even count → BA pairs (2 pairs shown; add more if you like)
EDITORIALS = [
    # Vanity BA
    {"image_url": "https://images.unsplash.com/photo-1529070538774-1843cb3265df?q=80&w=1600&auto=format&fit=crop", "caption": "Vanity — Before"},
    {"image_url": "https://images.unsplash.com/photo-1525286116112-b59af11adad1?q=80&w=1600&auto=format&fit=crop", "caption": "Vanity — After"},
    # Kitchen island BA
    {"image_url": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=1600&auto=format&fit=crop", "caption": "Island — Before"},
    {"image_url": "https://images.unsplash.com/photo-1505691723518-36a5ac3b2b8f?q=80&w=1600&auto=format&fit=crop", "caption": "Island — After"},
]

PROJECTS = [
    {
        "thumb_url": "https://images.unsplash.com/photo-1554995207-c18c203602cb?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1554995207-c18c203602cb?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Book-matched reception desk",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Island with mitred waterfall",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1523419409543-8b8d5a5f7f86?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1523419409543-8b8d5a5f7f86?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Stair treads & cladding",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Large-format feature wall",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1540575467063-178a50c2df87?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Hotel vanity & wet areas",
    },
]

BRANDS = [
    {"name": "Antolini",      "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Antolini",      "site_url": "https://www.antolini.com/"},
    {"name": "Cosentino",     "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Cosentino",     "site_url": "https://www.cosentino.com/"},
    {"name": "Lapitec",       "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Lapitec",       "site_url": "https://www.lapitec.com/"},
]

TESTIMONIALS = [
    {
        "author": "L. Saeed",
        "role_company": "Penthouse Owner, DIFC",
        "quote": "Their book-matching and miters are immaculate. Every junction feels intentional.",
        "headshot_url": "https://i.pravatar.cc/120?img=36",
    },
    {
        "author": "C. Haddad",
        "role_company": "Hotel Operations",
        "quote": "Clean sequencing and protection kept public areas open. Handover was on time and spotless.",
        "headshot_url": "https://i.pravatar.cc/120?img=44",
    },
]

FAQS = [
    {
        "question": "Is marble suitable for high-use kitchens and baths?",
        "answer": "Yes—with the right finish, sealing and care. We’ll recommend stones and sealers that balance performance with the look you want.",
    },
    {
        "question": "How do you handle stain and etch protection?",
        "answer": "We test sealers on your chosen slab and provide a care guide. Honed finishes can reduce the visibility of etching in wet areas.",
    },
    {
        "question": "Can you book-match large feature walls?",
        "answer": "Absolutely. We vein-map digitally, propose layout options and dry-lay for approval before cutting.",
    },
    {
        "question": "Typical lead times?",
        "answer": "Most scopes complete in 3–8 weeks depending on slab availability, edge profiles and site readiness.",
    },
    {
        "question": "Do you offer repairs or re-polish?",
        "answer": "Yes. We can re-hone/polish and re-seal, and replace damaged pieces if spares are available.",
    },
]

FEATURES_FOR_FALLBACK = [
    {"icon_class": "fa-solid fa-swatchbook",     "label": "Slab Curation"},
    {"icon_class": "fa-solid fa-ruler-combined", "label": "CNC Precision"},
    {"icon_class": "fa-solid fa-shapes",         "label": "Book-match Layouts"},
    {"icon_class": "fa-solid fa-shield-halved",  "label": "Sealed & Protected"},
]

INSIGHTS = [
    {
        "title": "Choosing stone that lasts in Dubai",
        "cover_image_url": "https://picsum.photos/1200/700?random=94001",
        "tag": "Materials",
        "excerpt": "Marble vs. quartzite vs. sintered stone—where each shines in heat, humidity and daily use.",
        "read_minutes": 5,
        "body": "Natural stones bring unmatched depth; engineered slabs add resilience. Start with location and use, then decide finish and sealer to match…",
    },
    {
        "title": "Book-matching 101",
        "cover_image_url": "https://picsum.photos/1200/700?random=94002",
        "tag": "Detailing",
        "excerpt": "Mirror vs. slip match, vein direction and where joints disappear.",
        "read_minutes": 4,
        "body": "Plan the hero surface first. Keep joints out of primary sight lines, align edges with reveals, and confirm everything in a dry-lay before cutting…",
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

    # Overview features (chips)
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
    print("Tip: Prefer transparent PNG/SVG brand logos for a cleaner row.")
