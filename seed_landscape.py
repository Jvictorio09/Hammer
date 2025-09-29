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

parser = argparse.ArgumentParser(description="Seed Landscape Service + related content")
parser.add_argument("--settings", help="Django settings module (e.g. myProject.settings)")
parser.add_argument("--title", default="Landscape Design & Build")
parser.add_argument("--slug", default="landscape-design-build")
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
# Content (taken from your latest page)
# -----------------------------------------------------------------------------

HERO_MEDIA = "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=2000&auto=format&fit=crop"

SERVICE_DEFAULTS = dict(
    eyebrow="Landscape",
    hero_headline="Quiet-Luxury Landscape Design & Build in Dubai",
    hero_subcopy=(
        "Native planting. Custom pools & pergolas. Architectural lighting. "
        "One integrated team—from concept to aftercare."
    ),
    hero_media_url=HERO_MEDIA,
    pinned_heading="Our Capability",
    pinned_title="End-to-end landscape design & build for modern living",
    pinned_body_1=(
        "Hammer Landscape delivers premium outdoor architecture in Dubai—custom pools, pergolas, lighting, "
        "water features and native planting—driven by innovative design and meticulous execution."
    ),
    pinned_body_2="One integrated contract from concept to aftercare. Weekly cadence. No surprises.",
    insights_heading="Insights",
    insights_subcopy="Ideas, guides, and updates from our landscape team.",
    stat_projects="650+",
    stat_years="20+",
    stat_specialists="1000+",
    seo_meta_title="Landscape Design & Build in Dubai | Hammer Group",
    seo_meta_description="Premium landscape design & build in Dubai. Native planting, custom pools, pergolas and architectural lighting—with fixed milestones and one accountable team.",
    canonical_path="/services/landscape-design-build/",
)

CAPABILITIES = [
    {
        "title": "Design Studio",
        "blurb": "Concept, 2D/3D, planting palettes, lighting scenes.",
        "icon_class": "fa-solid fa-compass-drafting",
    },
    {
        "title": "Technical & Drawings",
        "blurb": "Authority-ready packages with GA, details, BOQ, and full coordination.",
        "icon_class": "fa-solid fa-file-shield",
    },
    {
        "title": "Build & Delivery",
        "blurb": "One crew. Clear milestones. Clean sites.",
        "icon_class": "fa-solid fa-helmet-safety",
    },
    {
        "title": "Pools",
        "blurb": "Custom shells, resurfacing, filtration & automation, LED scenes & safety.",
        "icon_class": "fa-solid fa-water-ladder",
    },
    {
        "title": "Water Features",
        "blurb": "Rills, scuppers, sheet falls—engineered to whisper with low upkeep.",
        "icon_class": "fa-solid fa-water",
    },
    {
        "title": "Architectural Lighting",
        "blurb": "Layers that celebrate form—paths, trees, and water—glare controlled.",
        "icon_class": "fa-solid fa-lightbulb",
    },
]

# 4-step delivery rail (matches the page)
PROCESS = [
    {"step_no": 1, "title": "Site study & concept",       "description": "Survey, sun/wind analysis, native palette, 3D mood."},
    {"step_no": 2, "title": "Permits & technical",        "description": "MEP, structural, authority approvals, tender-ready drawings."},
    {"step_no": 3, "title": "Build & logistics",          "description": "One crew. Stone, decking, water features, lighting, planting."},
    {"step_no": 4, "title": "Handover & aftercare",       "description": "Snag-free delivery, irrigation tuning, seasonal lighting scenes."},
]

# Metrics – three cards shown on page
METRICS = [
    {"value": "650+",   "label": "Projects Delivered"},
    {"value": "20+ yrs","label": "Operating in Dubai"},
    {"value": "1000+",  "label": "In-house Specialists"},
]

# Editorials → used as Before/After pairs (2 pairs here; add more if you like)
EDITORIALS = [
    # Lighting BA
    {"image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?q=80&w=1600&auto=format&fit=crop", "caption": "Lighting: Before"},
    {"image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1600&auto=format&fit=crop", "caption": "Lighting: After"},
    # Pool BA
    {"image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1600&auto=format&fit=crop", "caption": "Pool: Before"},
    {"image_url": "https://images.unsplash.com/photo-1505852679233-d9fd70aff56d?q=80&w=1600&auto=format&fit=crop", "caption": "Pool: After"},
]

# Signature projects (5 cards, desktop grid + mobile reel)
PROJECTS = [
    {"thumb_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=800&auto=format&fit=crop",
     "full_url":  "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?q=80&w=1600&auto=format&fit=crop",
     "caption":   "Evening ambience"},
    {"thumb_url": "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=800&auto=format&fit=crop",
     "full_url":  "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=1600&auto=format&fit=crop",
     "caption":   "Pool & pergola"},
    {"thumb_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
     "full_url":  "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80",
     "caption":   "Native & low-water"},
    {"thumb_url": "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=800&auto=format&fit=crop",
     "full_url":  "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=1600&auto=format&fit=crop",
     "caption":   "Outdoor rooms"},
    {"thumb_url": "https://images.unsplash.com/photo-1542744173-05336fcc7ad4?auto=format&fit=crop&w=800&q=80",
     "full_url":  "https://images.unsplash.com/photo-1542744173-05336fcc7ad4?auto=format&fit=crop&w=1600&q=80",
     "caption":   "Architectural lighting"},
]

BRANDS = [
    {"name": "Cosentino",         "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Cosentino", "site_url": "https://www.cosentino.com/"},
    {"name": "Hunter Irrigation", "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Hunter",    "site_url": "https://www.hunterindustries.com/"},
    {"name": "Lutron",            "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Lutron",    "site_url": "https://www.lutron.com/"},
]

TESTIMONIALS = [
    {"author": "R. Al Mansoori", "role_company": "Private Villa Owner",
     "quote": "Hammer turned our yard into a resort. Clear schedule, zero surprises.", "headshot_url": "https://i.pravatar.cc/100?img=12"},
    {"author": "S. Haddad", "role_company": "Hospitality Director",
     "quote": "Their coordination between design and build saved us weeks.", "headshot_url": "https://i.pravatar.cc/100?img=22"},
    {"author": "M. Abed", "role_company": "Developer, Meydan",
     "quote": "Excellent quality control and communication—would award again.", "headshot_url": "https://i.pravatar.cc/100?img=31"},
]

FAQS = [
    {"question": "How soon can you start?",
     "answer": "Typically 2–4 weeks from concept sign-off. Authority approvals can extend timelines; we’ll surface that early and keep a transparent weekly cadence."},
    {"question": "Do you work with existing pools?",
     "answer": "Yes. We refresh surfaces and coping, add discreet architectural lighting, upgrade filtration/automation, and integrate planting without disrupting structure."},
    {"question": "What maintenance do you offer?",
     "answer": "Our aftercare team handles plant health, irrigation balancing, and seasonal lighting presets. We can also schedule deep cleans and re-mulching annually."},
    {"question": "Do you handle permits and authority approvals?",
     "answer": "Yes. Our engineering team prepares drawings and manages submissions end-to-end."},
]

FEATURES_FOR_FALLBACK = [
    {"icon_class": "fa-solid fa-pen-ruler",      "label": "2D / 3D Design"},
    {"icon_class": "fa-solid fa-draw-polygon",   "label": "Full Drawings"},
    {"icon_class": "fa-solid fa-mountain-sun",   "label": "Hardscape"},
    {"icon_class": "fa-solid fa-seedling",       "label": "Softscape"},
    {"icon_class": "fa-solid fa-water-ladder",   "label": "Pools"},
    {"icon_class": "fa-solid fa-water",          "label": "Water Features"},
    {"icon_class": "fa-solid fa-lightbulb",      "label": "Architectural Lighting"},
    {"icon_class": "fa-solid fa-people-group",   "label": "In-house Build Team"},
]

INSIGHTS = [
    {
        "title": "Planning a drought-smart garden in Dubai",
        "cover_image_url": "https://picsum.photos/1200/700?random=91001",
        "tag": "Landscape",
        "excerpt": "Water-wise planting and efficient irrigation—without losing the lush look.",
        "read_minutes": 5,
        "body": "Selecting regional natives and tuning irrigation zones can cut water use 35–50% while improving plant health...",
    },
    {
        "title": "Pool lighting: layers that enhance, never glare",
        "cover_image_url": "https://picsum.photos/1200/700?random=91002",
        "tag": "Lighting",
        "excerpt": "How to design pool and garden lighting scenes that feel cinematic and safe.",
        "read_minutes": 4,
        "body": "Think in layers: soft path markers, tree uplights, and low-glare underwater fixtures on separate scenes...",
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

    # Fallback features for Overview
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
