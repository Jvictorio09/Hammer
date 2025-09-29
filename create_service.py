import os
import sys

# -- Update if your settings module path differs --
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django
django.setup()

from django.db import transaction
from django.utils.text import slugify

# -- Update "myApp" if your app label is different --
from myApp.models import (
    Service,
    ServiceFeature,
    ServiceEditorialImage,
    ServiceProjectImage,
)

@transaction.atomic
def run():
    # ---------- Core service content (pulled from your template/copy) ----------
    slug = "landscape"

    service_defaults = {
        "title": "Landscape Design & Build",
        "eyebrow": "Landscape",
        "hero_headline": "Quiet-Luxury Landscape Design & Build in Dubai",
        "hero_subcopy": (
            "Native planting. Custom pools & pergolas. Architectural lighting. "
            "One integrated team—from concept to aftercare."
        ),
        "hero_media_url": "https://picsum.photos/1920/1080?random=2001",
        "stat_projects": "650+",
        "stat_years": "20+",
        "stat_specialists": "1000+",
        "pinned_heading": "Our Difference",
        "pinned_title": "Landscapes that live beautifully—day and night.",
        "pinned_body_1": (
            "We craft outdoor rooms that feel effortless to use and effortless to maintain. "
            "Expect native/low-water planting, precise stonework, and discreet lighting that "
            "celebrates the architecture."
        ),
        "pinned_body_2": (
            "With one integrated contract we own concept, permits, build and aftercare—"
            "delivering cost certainty and a clear weekly cadence of progress."
        ),
        "seo_meta_title": "Landscape Design & Build in Dubai | Hammer Group",
        "seo_meta_description": (
            "Premium landscape design & build in Dubai. Hammer Group creates timeless outdoor "
            "spaces—native planting, custom pools, pergolas and architectural lighting—with fixed "
            "milestones and one accountable team."
        ),
        "canonical_path": "/services/landscape/",
    }

    # ---------- Upsert Service ----------
    service, created = Service.objects.get_or_create(slug=slug, defaults=service_defaults)

    # If it already exists, update fields with latest copy
    for k, v in service_defaults.items():
        setattr(service, k, v)

    if not service.slug:
        service.slug = slugify(service.title or "service")

    service.save()

    # ---------- Replace Features ----------
    features = [
        # sort_order, icon_class, label
        (1, "fa-solid fa-seedling",        "Native / Low-water"),
        (2, "fa-solid fa-water-ladder",    "Custom Pools"),
        (3, "fa-solid fa-umbrella-beach",  "Pergolas & Decks"),
        (4, "fa-solid fa-lightbulb",       "Architectural Lighting"),
    ]

    # Clear and repopulate
    ServiceFeature.objects.filter(service=service).delete()
    ServiceFeature.objects.bulk_create([
        ServiceFeature(
            service=service,
            sort_order=so,
            icon_class=icon,
            label=label,
        )
        for (so, icon, label) in features
    ])

    # ---------- Replace Editorial Images (the “scroll column” trio) ----------
    editorial_images = [
        # sort_order, image_url, caption
        (1, "https://picsum.photos/1200/800?random=2211", "Evening ambience"),
        (2, "https://picsum.photos/1200/800?random=2212", "Native & low-water"),
        (3, "https://picsum.photos/1200/800?random=2213", "Outdoor rooms"),
    ]

    ServiceEditorialImage.objects.filter(service=service).delete()
    ServiceEditorialImage.objects.bulk_create([
        ServiceEditorialImage(
            service=service,
            sort_order=so,
            image_url=url,
            caption=cap,
        )
        for (so, url, cap) in editorial_images
    ])

    # ---------- Replace Project Images (the horizontal carousel) ----------
    project_images = [
        # sort_order, thumb_url, full_url, caption
        (1, "https://picsum.photos/800/600?random=2401", "https://picsum.photos/1600/1200?random=2401", "Landscape Project 01"),
        (2, "https://picsum.photos/800/600?random=2402", "https://picsum.photos/1600/1200?random=2402", "Landscape Project 02"),
        (3, "https://picsum.photos/800/600?random=2403", "https://picsum.photos/1600/1200?random=2403", "Landscape Project 03"),
        (4, "https://picsum.photos/800/600?random=2404", "https://picsum.photos/1600/1200?random=2404", "Landscape Project 04"),
        (5, "https://picsum.photos/800/600?random=2405", "https://picsum.photos/1600/1200?random=2405", "Landscape Project 05"),
        (6, "https://picsum.photos/800/600?random=2406", "https://picsum.photos/1600/1200?random=2406", "Landscape Project 06"),
    ]

    ServiceProjectImage.objects.filter(service=service).delete()
    ServiceProjectImage.objects.bulk_create([
        ServiceProjectImage(
            service=service,
            sort_order=so,
            thumb_url=thumb,
            full_url=full,
            caption=cap,
        )
        for (so, thumb, full, cap) in project_images
    ])

    print(f"{'✅ Created' if created else '✅ Updated'}: Service '{service.title}' ({service.slug})")
    print(f"   → Features: {len(features)}")
    print(f"   → Editorial images: {len(editorial_images)}")
    print(f"   → Project images: {len(project_images)}")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("❌ Seeding failed:", e)
        sys.exit(1)
