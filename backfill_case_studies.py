#!/usr/bin/env python3
"""
Backfill CaseStudy rows from existing Service content.

Usage:
  python backfill_case_studies.py --settings myProject.settings
  python backfill_case_studies.py --settings myProject.settings --service "landscape-design-build"
  python backfill_case_studies.py --settings myProject.settings --service "Interior Design & Build"
  python backfill_case_studies.py --settings myProject.settings --dry-run --rebuild-missing-only
  python backfill_case_studies.py --help

Notes:
- Idempotent-friendly. Use --rebuild-missing-only to avoid duplicates.
- Picks hero image from Service.hero_media_url → first Editorial → first Project full_url → thumb_url.
"""

import os
import sys
import argparse
from pathlib import Path

# -----------------------------------------------------------------------------
# Django bootstrap (same pattern as your seed script)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Backfill CaseStudy rows from existing Services")
parser.add_argument("--settings", help="Django settings module (e.g. myProject.settings)")
parser.add_argument("--service", help="Limit to one service by slug OR exact title")
parser.add_argument("--dry-run", action="store_true", help="Print actions without writing to DB")
parser.add_argument("--rebuild-missing-only", action="store_true",
                    help="Create CaseStudy only when service has none")
parser.add_argument("--no-feature-toggle", action="store_true",
                    help="Do not auto-set is_featured=True on the first created case study")
parser.add_argument("--max-feature-tags", type=int, default=6, help="Max feature labels to put into tags_csv")
parser.add_argument("--default-scope", default="Design + Build")
parser.add_argument("--default-status", default="Completed")
args = parser.parse_args()

if args.settings:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)
elif not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django  # noqa: E402
django.setup()

from django.db import transaction  # noqa: E402
from django.utils.text import slugify  # noqa: E402

from myApp.models import (  # noqa: E402
    Service, ServiceEditorialImage, ServiceProjectImage, ServiceFeature, CaseStudy
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def best_image_for_service(svc: Service) -> str:
    if svc.hero_media_url:
        return svc.hero_media_url
    editorial = (ServiceEditorialImage.objects
                 .filter(service=svc)
                 .order_by("sort_order", "id")
                 .values_list("image_url", flat=True)
                 .first())
    if editorial:
        return editorial
    proj_full = (ServiceProjectImage.objects
                 .filter(service=svc)
                 .order_by("sort_order", "id")
                 .values_list("full_url", flat=True)
                 .first())
    if proj_full:
        return proj_full
    proj_thumb = (ServiceProjectImage.objects
                  .filter(service=svc)
                  .order_by("sort_order", "id")
                  .values_list("thumb_url", flat=True)
                  .first())
    return proj_thumb or ""

def tags_from_features(svc: Service, limit: int) -> str:
    labels = list(
        ServiceFeature.objects
        .filter(service=svc)
        .order_by("sort_order", "id")
        .values_list("label", flat=True)[:limit]
    )
    return ", ".join([l for l in labels if l])

def summary_for_service(svc: Service) -> str:
    if svc.hero_subcopy:
        return svc.hero_subcopy
    if svc.pinned_body_1:
        return svc.pinned_body_1
    if svc.pinned_body_2:
        return svc.pinned_body_2
    return f"{svc.eyebrow or ''} {svc.title}".strip()

def pick_services(selector: str | None):
    qs = Service.objects.all().order_by("sort_order", "title")
    if not selector:
        return list(qs)
    # Try slug first, then exact title
    svc = qs.filter(slug=selector).first()
    if svc:
        return [svc]
    svc = qs.filter(title=selector).first()
    if svc:
        return [svc]
    print(f"[!] No Service found for '{selector}'. Exiting.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
@transaction.atomic
def backfill(services, *, dry_run=False, missing_only=False,
             no_feature_toggle=False, max_feature_tags=6,
             default_scope="Design + Build", default_status="Completed"):
    created_total = 0
    featured_marked = False

    # 1) Ensure slugs
    for svc in services:
        if not svc.slug:
            old = svc.slug
            svc.slug = slugify(svc.title or f"service-{svc.pk}")[:200]
            print(f"[i] Slug backfill: Service[{svc.pk}] '{svc.title}': '{old}' -> '{svc.slug}'")
            if not dry_run:
                svc.save(update_fields=["slug"])

    # 2) Create CaseStudy rows
    for svc in services:
        existing = CaseStudy.objects.filter(service=svc)
        if missing_only and existing.exists():
            print(f"[=] Skip: '{svc.title}' already has {existing.count()} case study(ies).")
            continue

        hero_url = best_image_for_service(svc)
        if not hero_url:
            print(f"[!] '{svc.title}' has no image candidates; will create with empty hero_image_url.")

        title = svc.title
        slug_val = slugify(title)[:240]
        # Avoid duplicate slug per service when missing_only=False
        if existing.filter(slug=slug_val).exists():
            slug_val = slugify(f"{title}-{svc.pk}")[:240]

        payload = dict(
            service=svc,
            title=title,
            slug=slug_val,
            hero_image_url=hero_url,
            summary=summary_for_service(svc),
            scope=default_scope,
            size_label="",
            timeline_label="",
            status_label=default_status,
            tags_csv=tags_from_features(svc, limit=max_feature_tags),
            is_featured=False,
            sort_order=svc.sort_order,
        )

        if dry_run:
            print(f"[DRY] Would create CaseStudy for '{svc.title}' (slug='{slug_val}', featured={(not no_feature_toggle and not featured_marked)})")
            if not no_feature_toggle and not featured_marked:
                featured_marked = True
            created_total += 1
            continue

        cs = CaseStudy.objects.create(**payload)
        created_total += 1
        print(f"[+] Created CaseStudy[{cs.pk}] for '{svc.title}'")

        if not no_feature_toggle and not featured_marked:
            cs.is_featured = True
            cs.save(update_fields=["is_featured"])
            featured_marked = True
            print(f"[★] Marked CaseStudy[{cs.pk}] as featured")

    print(f"\n✔ Backfill complete. {'(dry run) ' if dry_run else ''}Created: {created_total}")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    target_services = pick_services(args.service)
    backfill(
        target_services,
        dry_run=args.dry_run,
        missing_only=args.rebuild_missing_only,
        no_feature_toggle=args.no_feature_toggle,
        max_feature_tags=args.max_feature_tags,
        default_scope=args.default_scope,
        default_status=args.default_status,
    )
