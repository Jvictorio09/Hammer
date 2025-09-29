#!/usr/bin/env python3
"""
Seed a complete 'Facility Management & Aftercare' Service page with rich, production-level content.

Usage:
  python seed_facility.py --settings myProject.settings
  python seed_facility.py --settings myProject.settings --wipe
  python seed_facility.py --settings myProject.settings --title "Facility Management & Aftercare" --slug "facility-management"

Notes:
- Idempotent: existing rows are updated in place (unless --wipe).
- Content emphasizes Hard + Soft Services, uptime, compliance, and transparent reporting.
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

parser = argparse.ArgumentParser(description="Seed Facility Management Service + related content")
parser.add_argument("--settings", help="Django settings module (e.g. myProject.settings)")
parser.add_argument("--title", default="Facility Management & Aftercare")
parser.add_argument("--slug", default="facility-management")
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
# Content (Hard + Soft services; uptime + cleanliness)
# -----------------------------------------------------------------------------

HERO_MEDIA = "https://images.unsplash.com/photo-1581091870622-7b1c1ae0f15b?q=80&w=2000&auto=format&fit=crop"

SERVICE_DEFAULTS = dict(
    eyebrow="Facilities",
    hero_headline="Facility Management & Aftercare in Dubai",
    hero_subcopy=(
        "Aftercare should never be an afterthought. Hammer’s dedicated hard- and soft-services teams protect your "
        "most valuable assets—keeping power, water and HVAC systems reliable while maintaining clean, safe spaces "
        "for people to work and thrive."
    ),
    hero_media_url=HERO_MEDIA,
    pinned_heading="Our Capability",
    pinned_title="Uptime, cleanliness, and compliance—delivered by one accountable team.",
    pinned_body_1=(
        "From MEP and HVAC to daily housekeeping, we plan preventive maintenance, respond 24/7, and report with "
        "transparency. Assets are tracked, tasks are sequenced, and SLAs are visible in plain language."
    ),
    pinned_body_2="Engineers, supervisors and soft-services leads under a single contract and weekly cadence.",
    insights_heading="Insights",
    insights_subcopy="Guides on PPM, energy optimization and compliance for Dubai facilities.",
    stat_projects="120+ sites",
    stat_years="20+ yrs",
    stat_specialists="100+ technicians",
    seo_meta_title="Facility Management & Aftercare in Dubai | Hammer Group",
    seo_meta_description=(
        "Hard & soft facility management in Dubai—HVAC, MEP, electrical, plumbing, cleaning and hygiene—"
        "with preventive maintenance, 24/7 response and transparent SLA reporting."
    ),
    canonical_path="/services/facility-management/",
)

CAPABILITIES = [
    {
        "title": "Hard Services (MEP/HVAC/Electrical/Plumbing)",
        "blurb": "Planned preventive maintenance, breakdown response and lifecycle replacements across critical systems.",
        "icon_class": "fa-solid fa-gears",
    },
    {
        "title": "Soft Services (Cleaning & Hygiene)",
        "blurb": "Daily schedules, periodic deep cleans and high-touch sanitation with measurable quality checks.",
        "icon_class": "fa-solid fa-broom",
    },
    {
        "title": "PPM Planning & CMMS",
        "blurb": "Digitized asset registers, task libraries, QR tagging and audit trails for every intervention.",
        "icon_class": "fa-solid fa-clipboard-check",
    },
    {
        "title": "Energy & Performance",
        "blurb": "HVAC tuning, BMS coordination and retrofit recommendations to cut consumption and downtime.",
        "icon_class": "fa-solid fa-bolt",
    },
    {
        "title": "HSE & Compliance",
        "blurb": "Permits-to-work, RAMS, statutory inspections and authority coordination built into the plan.",
        "icon_class": "fa-solid fa-shield-heart",
    },
    {
        "title": "24/7 Helpdesk & Response",
        "blurb": "Tiered SLAs with escalation paths, spare parts strategy and on-call coverage.",
        "icon_class": "fa-solid fa-headset",
    },
]

# Exactly 4 steps per your note
PROCESS = [
    {"step_no": 1, "title": "Mobilization & Asset Audit", "description": "Onboarding, asset register build, condition survey and risk map."},
    {"step_no": 2, "title": "PPM & Schedules",            "description": "Calendarized hard- and soft-service tasks with documented methods."},
    {"step_no": 3, "title": "Delivery & Response",         "description": "Daily routines, periodic tasks and 24/7 call-outs with SLA tracking."},
    {"step_no": 4, "title": "Reporting & Improvement",     "description": "Monthly dashboards, findings, energy insights and continuous improvement."},
]

METRICS = [
    {"value": "99.5%",      "label": "Critical Uptime"},
    {"value": "24/7",       "label": "Rapid Response"},
    {"value": "98%",        "label": "SLA Compliance"},
]

# Even count → BA pairs (before/after for soft-services + plant rooms)
EDITORIALS = [
    {"image_url": "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?q=80&w=1600&auto=format&fit=crop", "caption": "Lobby — Before"},
    {"image_url": "https://images.unsplash.com/photo-1505691723518-36a5ac3b2b8f?q=80&w=1600&auto=format&fit=crop", "caption": "Lobby — After"},
    {"image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=1600&auto=format&fit=crop", "caption": "Plant Room — Before"},
    {"image_url": "https://images.unsplash.com/photo-1581093588401-16a1d3f0b7cf?q=80&w=1600&auto=format&fit=crop", "caption": "Plant Room — After"},
]

# Signature sites (illustrative)
PROJECTS = [
    {
        "thumb_url": "https://images.unsplash.com/photo-1523359346063-d879354c0ea5?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1523359346063-d879354c0ea5?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Corporate HQ — MEP & Soft Services",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1557244053-23d685287bc3?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1557244053-23d685287bc3?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Healthcare — Cleanliness & Compliance",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Retail Mall — Uptime & Energy",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1507209696998-3c532be9b2b1?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1507209696998-3c532be9b2b1?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Hospitality — Guest Areas",
    },
    {
        "thumb_url": "https://images.unsplash.com/photo-1521791055366-0d553872125f?q=80&w=800&auto=format&fit=crop",
        "full_url":  "https://images.unsplash.com/photo-1521791055366-0d553872125f?q=80&w=1600&auto=format&fit=crop",
        "caption":   "Industrial — Critical Systems",
    },
]

BRANDS = [
    {"name": "Siemens",   "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Siemens",   "site_url": "https://www.siemens.com/"},
    {"name": "Honeywell", "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Honeywell", "site_url": "https://www.honeywell.com/"},
    {"name": "Nilfisk",   "logo_url": "https://dummyimage.com/240x80/eeeeee/111111&text=Nilfisk",   "site_url": "https://www.nilfisk.com/"},
]

TESTIMONIALS = [
    {
        "author": "A. Khan",
        "role_company": "Facilities Director, Corporate HQ",
        "quote": "Uptime and cleanliness improved within the first quarter—backed by clear dashboards.",
        "headshot_url": "https://i.pravatar.cc/120?img=17",
    },
    {
        "author": "L. Ortega",
        "role_company": "Operations Manager, Healthcare",
        "quote": "PPM discipline is excellent. Audits are smooth and escalations are fast and professional.",
        "headshot_url": "https://i.pravatar.cc/120?img=23",
    },
]

FAQS = [
    {
        "question": "Do you manage both hard and soft services under one contract?",
        "answer": "Yes. MEP/HVAC/electrical/plumbing plus cleaning and hygiene are coordinated by one team with a single SLA set.",
    },
    {
        "question": "What’s included in your PPM plan?",
        "answer": "Calendarized tasks per asset category, method statements, spares strategy, and statutory inspections with proof of completion.",
    },
    {
        "question": "Can you operate in live environments?",
        "answer": "Absolutely. We phase works, protect finishes, and schedule noisy tasks off-peak to keep business moving.",
    },
    {
        "question": "How do we see performance?",
        "answer": "Monthly reports show completed tasks, response times, SLA compliance, incidents and improvement actions.",
    },
]

# Feature chips to ensure the overview has content even on day one
FEATURES_FOR_FALLBACK = [
    {"icon_class": "fa-solid fa-toolbox",          "label": "Reactive & Planned"},
    {"icon_class": "fa-solid fa-qrcode",           "label": "QR Asset Tags"},
    {"icon_class": "fa-solid fa-gauge-high",       "label": "Energy Tuning"},
    {"icon_class": "fa-solid fa-user-shield",      "label": "HSE First"},
]

INSIGHTS = [
    {
        "title": "PPM vs. Reactive: why uptime wins",
        "cover_image_url": "https://picsum.photos/1200/700?random=95001",
        "tag": "Operations",
        "excerpt": "Preventive maintenance reduces failures, extends asset life and cuts total cost of ownership.",
        "read_minutes": 4,
        "body": "Start with criticality analysis. Build a realistic calendar, then enforce closeout and feedback loops to refine frequencies over time…",
    },
    {
        "title": "Cleanliness that clients notice",
        "cover_image_url": "https://picsum.photos/1200/700?random=95002",
        "tag": "Soft Services",
        "excerpt": "High-touch points, smart scheduling and visible standards raise satisfaction scores.",
        "read_minutes": 3,
        "body": "Blend daily routes with periodic deep cleans, measure what matters, and share simple scorecards that everyone can read at a glance…",
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

    # Process steps (exactly 4)
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

    # Overview features
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
    print("Tip: Keep editorial images in even counts so the Before/After panel renders as clean pairs.")
    print("Tip: Prefer transparent PNG/SVG brand logos for the cleanest row.")
