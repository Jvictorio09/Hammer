#!/usr/bin/env python
"""
Render a service detail page (e.g., “Landscape Dubai”) straight from the database.

Usage:
    python export_service_page.py
    SERVICE_SLUG=interior-design-build python export_service_page.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "myProject"
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django  # noqa: E402

django.setup()

from django.core.exceptions import ObjectDoesNotExist  # noqa: E402
from django.db.models import Prefetch  # noqa: E402
from django.template.loader import render_to_string  # noqa: E402
from django.utils import timezone  # noqa: E402

from myApp.models import (  # noqa: E402
    CaseStudy,
    Insight,
    Service,
    ServiceCapability,
    ServiceEditorialImage,
    ServiceFAQ,
    ServiceFeature,
    ServiceMetric,
    ServicePartnerBrand,
    ServiceProcessStep,
    ServiceProjectImage,
    ServiceTestimonial,
)

DEFAULT_SLUG = "landscape-design-build"
SERVICE_SLUG = os.getenv("SERVICE_SLUG", DEFAULT_SLUG)
OUTPUT_DIR = Path(__file__).resolve().parent / "exports"


def load_service(slug: str) -> Service:
    """Fetch the service with all related content needed for rendering."""
    return Service.objects.prefetch_related(
        Prefetch(
            "features",
            queryset=ServiceFeature.objects.only(
                "id",
                "service_id",
                "sort_order",
                "icon_class",
                "label",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "editorial_images",
            queryset=ServiceEditorialImage.objects.only(
                "id",
                "service_id",
                "sort_order",
                "image_url",
                "caption",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "project_images",
            queryset=ServiceProjectImage.objects.only(
                "id",
                "service_id",
                "sort_order",
                "thumb_url",
                "full_url",
                "caption",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "case_studies",
            queryset=CaseStudy.objects.only(
                "id",
                "service_id",
                "title",
                "slug",
                "hero_image_url",
                "thumb_url",
                "full_url",
                "summary",
                "sort_order",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "capabilities",
            queryset=ServiceCapability.objects.only(
                "id",
                "service_id",
                "sort_order",
                "title",
                "blurb",
                "icon_class",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "process_steps",
            queryset=ServiceProcessStep.objects.only(
                "id",
                "service_id",
                "sort_order",
                "step_no",
                "title",
                "description",
            ).order_by("sort_order", "step_no", "id"),
        ),
        Prefetch(
            "metrics",
            queryset=ServiceMetric.objects.only(
                "id",
                "service_id",
                "sort_order",
                "value",
                "label",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "faqs",
            queryset=ServiceFAQ.objects.only(
                "id",
                "service_id",
                "sort_order",
                "question",
                "answer",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "partner_brands",
            queryset=ServicePartnerBrand.objects.only(
                "id",
                "service_id",
                "sort_order",
                "name",
                "logo_url",
                "site_url",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "testimonials",
            queryset=ServiceTestimonial.objects.only(
                "id",
                "service_id",
                "sort_order",
                "author",
                "role_company",
                "quote",
                "headshot_url",
            ).order_by("sort_order", "id"),
        ),
        Prefetch(
            "insights",
            queryset=Insight.objects.filter(
                published=True,
                is_active=True,
                published_at__lte=timezone.now(),
            )
            .select_related("author")
            .only(
                "id",
                "service_id",
                "title",
                "slug",
                "tag",
                "excerpt",
                "cover_image_url",
                "read_minutes",
                "published_at",
                "author",
                "created_at",
            )
            .order_by("-published_at", "-created_at"),
            to_attr="prefetched_insights",
        ),
    ).get(slug=slug)


def build_context(service: Service) -> dict:
    """Prepare the template context just like the live view."""
    editorial = list(service.editorial_images.all())
    ba_pairs = [
        (editorial[i], editorial[i + 1]) for i in range(0, len(editorial) - 1, 2)
    ]
    insights = getattr(service, "prefetched_insights", [])[:4]

    return {
        "service": service,
        "ba_pairs": ba_pairs,
        "insights": insights,
        "fallback_metrics": [
            {"value": service.stat_projects or "650+", "label": "Projects Delivered"},
            {"value": service.stat_years or "20+ yrs", "label": "Operating in Dubai"},
            {
                "value": service.stat_specialists or "1000+",
                "label": "In-house Specialists",
            },
        ],
    }


def main() -> None:
    try:
        service = load_service(SERVICE_SLUG)
    except ObjectDoesNotExist:
        raise SystemExit(f"Service with slug '{SERVICE_SLUG}' was not found.")

    context = build_context(service)
    html = render_to_string("services/service_detail.html", context)

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{SERVICE_SLUG}.html"
    output_path.write_text(html, encoding="utf-8")

    print(f"Rendered service page written to {output_path}")


if __name__ == "__main__":
    main()

