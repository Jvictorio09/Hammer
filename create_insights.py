# create_insights.py
from __future__ import annotations
import os
import sys
import typing as t

import django
from django.utils import timezone
from django.utils.text import slugify

# --- Django setup (so you can run standalone) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
django.setup()

from myApp.models import Service, Insight


def unique_slug(base: str) -> str:
    """
    Make a globally-unique slug for Insight by suffixing -2, -3, ...
    """
    seed = slugify(base)[:60] or "post"
    if not Insight.objects.filter(slug=seed).exists():
        return seed
    i = 2
    while True:
        trial = f"{seed}-{i}"
        if not Insight.objects.filter(slug=trial).exists():
            return trial
        i += 1


# ---- Your Insights seed data ----
LANDSCAPE_POSTS: t.List[dict] = [
    {
        "title": "Before You Pour Concrete: Levels, Drainage & Soil",
        "tag": "Siteworks",
        "read_minutes": 6,
        "excerpt": "The three checks that prevent heaving, ponding and tile failure: levels, sub-base, and positive drainage—with simple field tests you can do in minutes.",
        "cover_image_url": "https://images.unsplash.com/photo-1523419409543-a5e549c1c5b0?q=80&w=1200&auto=format&fit=crop",
        "body": "<p>Once concrete is down, mistakes are expensive. Verify levels, soil, and drainage before formwork.</p>",
    },
    {
        "title": "Plant Palette for Heat: Tough, Beautiful, Low-Water",
        "tag": "Planting",
        "read_minutes": 5,
        "excerpt": "Designer picks that survive hot, windy sites without looking ‘municipal’. Includes spacing, mulch, and irrigation notes for year-one success.",
        "cover_image_url": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=1200&auto=format&fit=crop",
        "body": "<p>Mix structure (evergreen) with seasonality. Right spacing + mulch beats oversizing irrigation.</p>",
    },
    {
        "title": "Light Your Garden Like a Hotel Courtyard",
        "tag": "Lighting",
        "read_minutes": 4,
        "excerpt": "Layered lighting that’s flattering, safe, and power-efficient: beam angles, color temps, and where to hide the fixtures.",
        "cover_image_url": "https://images.unsplash.com/photo-1506377295352-e3154d43ea9a?q=80&w=1200&auto=format&fit=crop",
        "body": "<p>Ambient, task, and accent layers. Hide the source; light the surface. CRI ≥ 90 for planting.</p>",
    },
    {
        "title": "From Sketch to Handover: Our Landscape Build Playbook",
        "tag": "Process",
        "read_minutes": 7,
        "excerpt": "Milestones, sign-offs, and the QA forms we use so projects finish cleanly—no last-week scrambles.",
        "cover_image_url": "https://images.unsplash.com/photo-1520975922325-24c47df9ae88?q=80&w=1200&auto=format&fit=crop",
        "body": "<p>Milestones: DD freeze, procurement lock, mock-ups, pre-hides, softscape, and handover.</p>",
    },
]


def seed_insights(service_slug: str = "landscape-design-build", reset: bool = False) -> None:
    try:
        svc = Service.objects.get(slug=service_slug)
    except Service.DoesNotExist:
        print(f"✗ Service with slug '{service_slug}' not found. Create it first.")
        return

    if reset:
        deleted = Insight.objects.filter(service=svc).delete()[0]
        print(f"• Deleted {deleted} existing insights for '{service_slug}'")

    created = 0
    for p in LANDSCAPE_POSTS:
        slug = unique_slug(p["title"])
        obj, was_created = Insight.objects.get_or_create(
            service=svc,
            title=p["title"],
            defaults={
                "slug": slug,
                "tag": p["tag"],
                "read_minutes": p["read_minutes"],
                "excerpt": p["excerpt"],
                "cover_image_url": p["cover_image_url"],
                "body": p["body"],
                "published": True,
                "published_at": timezone.now(),
            },
        )
        if was_created:
            created += 1

    total = Insight.objects.filter(service=svc).count()
    print(f"✓ Seeded {created} new insights for '{service_slug}'. Total now: {total}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed insights for a service")
    parser.add_argument("--service", default="landscape-design-build", help="Service slug")
    parser.add_argument("--reset", action="store_true", help="Delete existing insights before seeding")
    args = parser.parse_args()

    seed_insights(args.service, args.reset)
