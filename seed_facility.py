#!/usr/bin/env python3
"""
Seed 'Facility Management & Aftercare' Service from local images → Cloudinary → DB.

Usage:
  python seed_facility.py --settings myProject.settings ^
    --service-slug facility-management ^
    --root "E:\\New Downloads\\Hammer\\Facility Management" ^
    --cloud-folder hammer/facility ^
    --wipe

Notes:
- Idempotent: existing rows are updated (unless --wipe).
- Seeds "service showcases" as CaseStudy objects (team in action, not completed projects).
- Images are distributed equally across the 6 showcases.
"""

import os
import sys
import io
import argparse
import hashlib
from datetime import date
from pathlib import Path
from typing import List, Tuple, Optional

# -----------------------------------------------------------------------------
# Django bootstrap
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Seed Facility Management & Aftercare Service")
parser.add_argument("--settings", help="Django settings module (e.g., myProject.settings)")
parser.add_argument("--service-id", type=int, help="Service ID to update")
parser.add_argument("--service-slug", help="Service slug to update")
parser.add_argument("--root", required=True, help=r'Root folder, e.g., "E:\New Downloads\Hammer\Facility Management"')
parser.add_argument("--cloud-folder", default="hammer/facility", help="Cloudinary folder prefix")
parser.add_argument("--wipe", action="store_true", help="Delete existing related rows first")
parser.add_argument("--dry-run", action="store_true", help="Print actions; no uploads, no DB writes")
args = parser.parse_args()

if args.settings:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)
elif not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")

import django  # noqa: E402
django.setup()

from django.db import transaction  # noqa: E402
from myApp.models import (  # noqa: E402
    Service,
    ServiceCapability,
    ServiceMetric,
    ServiceProcessStep,
    ServiceFAQ,
    CaseStudy,
)

# -----------------------------------------------------------------------------
# Image Utilities
# -----------------------------------------------------------------------------
def ensure_pillow():
    try:
        import PIL  # noqa
    except Exception:
        raise RuntimeError("Pillow is required. Install with: pip install Pillow")


def ensure_cloudinary():
    try:
        import cloudinary  # noqa
        import cloudinary.uploader  # noqa
    except Exception:
        raise RuntimeError("cloudinary is required. Install with: pip install cloudinary")

    has_url = bool(os.getenv("CLOUDINARY_URL"))
    has_parts = all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET"),
    ])
    if not (has_url or has_parts):
        raise RuntimeError(
            "Missing Cloudinary credentials. Set CLOUDINARY_URL or "
            "CLOUDINARY_CLOUD_NAME / CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET."
        )


def slugify(text: str) -> str:
    import re
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def file_md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def load_and_precompress(path: Path, max_side=1920, jpeg_q=82, max_file_size=8*1024*1024) -> Tuple[bytes, str]:
    from PIL import Image, ImageOps

    im = Image.open(path)
    im = ImageOps.exif_transpose(im)

    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")

    w, h = im.size
    if max(w, h) > max_side:
        if w >= h:
            new_w = max_side
            new_h = int(h * (max_side / w))
        else:
            new_h = max_side
            new_w = int(w * (max_side / h))
        im = im.resize((new_w, new_h), Image.LANCZOS)

    has_alpha = (im.mode == "RGBA")
    
    if not has_alpha:
        im = im.convert("RGB")
        # Try initial quality, then reduce if file is too large
        quality = jpeg_q
        for attempt in range(3):
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
            data = buf.getvalue()
            if len(data) <= max_file_size:
                return data, "jpg"
            # File too large, reduce quality and try again
            quality = max(60, quality - 15)
        # If still too large after 3 attempts, resize more aggressively
        new_w = int(im.width * 0.75)
        new_h = int(im.height * 0.75)
        im = im.resize((new_w, new_h), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=75, optimize=True, progressive=True)
        return buf.getvalue(), "jpg"
    else:
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "png"


def cloudinary_upload(data_bytes: bytes, public_id: str, folder: Optional[str], overwrite=True) -> dict:
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    full_public_id = f"{folder}/{public_id}" if folder else public_id

    resp = cloudinary.uploader.upload(
        io.BytesIO(data_bytes),
        public_id=full_public_id,
        overwrite=overwrite,
        resource_type="image",
        use_filename=True,
        unique_filename=False,
        folder=folder or None,
        quality="auto:good",
        format="jpg",
    )
    return resp


def cloudinary_variant(base_url: str, width: int, height: int, crop="fill", gravity="auto") -> str:
    if "/upload/" not in base_url:
        return base_url
    trans = f"c_{crop},g_{gravity},w_{width},h_{height},f_auto,q_auto:good"
    return base_url.replace("/upload/", f"/upload/{trans}/", 1)


def discover_images(root: Path) -> List[Path]:
    imgs = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.JPEG", "*.PNG", "*.WEBP"):
        imgs.extend(sorted(root.glob(ext)))
    return imgs


def upsert(instance, data: dict, fields: list) -> bool:
    changed = False
    for f in fields:
        if hasattr(instance, f):
            old = getattr(instance, f, None)
            new = data.get(f, old)
            if old != new:
                setattr(instance, f, new)
                changed = True
    if changed:
        instance.save()
    return changed


# -----------------------------------------------------------------------------
# Service Showcases Metadata
# -----------------------------------------------------------------------------
SHOWCASES_META = [
    {
        "title": "24/7 Emergency Response Team",
        "summary": "Rapid response team available around the clock for critical facility issues.",
        "description": "Our dedicated emergency response team is available 24/7 to handle urgent facility issues. From MEP failures to critical system breakdowns, we deploy trained technicians within 2 hours to minimize downtime and protect your assets.",
        "tags_csv": "Emergency, 24/7, Response, MEP",
        "is_featured": True,
        "sort_order": 1,
    },
    {
        "title": "MEP Systems Management",
        "summary": "Expert maintenance of mechanical, electrical, and plumbing systems.",
        "description": "Comprehensive MEP system management ensures 98% uptime. Our certified technicians perform preventive maintenance, inspections, and repairs on HVAC, electrical panels, fire safety systems, and plumbing infrastructure to keep your facility running smoothly.",
        "tags_csv": "MEP, HVAC, Electrical, Plumbing",
        "is_featured": True,
        "sort_order": 2,
    },
    {
        "title": "Soft Services Excellence",
        "summary": "Professional cleaning, waste management, and facility hygiene services.",
        "description": "Our soft services team maintains immaculate commercial spaces through systematic cleaning protocols, waste management, pest control, and hygiene services. Trained staff use eco-friendly products and follow international standards for workplace safety and cleanliness.",
        "tags_csv": "Cleaning, Hygiene, Waste Management, Soft Services",
        "is_featured": False,
        "sort_order": 3,
    },
    {
        "title": "Pool & Landscape Care",
        "summary": "Ongoing pool maintenance and landscape upkeep for lasting beauty.",
        "description": "Specialized pool technicians perform chemical balancing, filtration checks, and equipment servicing. Landscape teams handle irrigation, pruning, seasonal planting, and pest control to preserve outdoor investments year-round.",
        "tags_csv": "Pool, Landscape, Maintenance, Irrigation",
        "is_featured": False,
        "sort_order": 4,
    },
    {
        "title": "Preventive Maintenance Program",
        "summary": "Scheduled inspections and maintenance to prevent costly breakdowns.",
        "description": "Our preventive maintenance program identifies issues before they become emergencies. Scheduled inspections, filter replacements, lubrication, calibration, and system testing extend equipment lifespan and reduce unexpected downtime.",
        "tags_csv": "Preventive, Maintenance, Inspections, Planning",
        "is_featured": False,
        "sort_order": 5,
    },
    {
        "title": "Quality Control & Inspections",
        "summary": "Rigorous quality checks and detailed reporting for accountability.",
        "description": "Every service is followed by quality control inspections and detailed reporting. Digital checklists, photo documentation, and performance metrics ensure transparency and continuous improvement across all facility operations.",
        "tags_csv": "Quality, Inspections, Reporting, Accountability",
        "is_featured": False,
        "sort_order": 6,
    },
]


# -----------------------------------------------------------------------------
# Main Seeder
# -----------------------------------------------------------------------------
def main():
    ensure_pillow()
    ensure_cloudinary()

    # Locate Service
    svc = None
    if args.service_id:
        svc = Service.objects.filter(id=args.service_id).first()
    elif args.service_slug:
        svc = Service.objects.filter(slug=args.service_slug).first()
    else:
        svc = Service.objects.filter(slug="facility-management").first()

    if not svc:
        print("[!] No Service found. Create 'Facility Management' service first or use --service-slug.")
        sys.exit(1)

    root = Path(args.root)
    if not root.exists():
        print(f"[!] Root folder not found: {root}")
        sys.exit(1)

    # Discover all images
    all_images = discover_images(root)
    if not all_images:
        print(f"[!] No images found in: {root}")
        sys.exit(1)

    print(f"[i] Seeding Facility Management for Service: {getattr(svc, 'title', svc.id)}")
    print(f"[i] Found {len(all_images)} images total")
    print(f"[i] Distributing equally across {len(SHOWCASES_META)} showcases")

    # Distribute images equally
    images_per_showcase = len(all_images) // len(SHOWCASES_META)
    remainder = len(all_images) % len(SHOWCASES_META)
    
    distributed = []
    idx = 0
    for i, meta in enumerate(SHOWCASES_META):
        count = images_per_showcase + (1 if i < remainder else 0)
        showcase_images = all_images[idx:idx + count]
        distributed.append((meta, showcase_images))
        idx += count

    with transaction.atomic():
        if args.wipe:
            print("[!] Wiping existing related rows…")
            svc.capabilities.all().delete()
            svc.metrics.all().delete()
            svc.process_steps.all().delete()
            svc.faqs.all().delete()
            svc.case_studies.all().delete()

        # Update Service hero/description
        if not args.dry_run:
            changed = upsert(
                svc,
                {
                    "title": "Facility Management & Aftercare",
                    "hero_headline": "Aftercare Should Not Be an Afterthought",
                    "hero_subcopy": "Hammer has a dedicated team of experts in soft and hard services focused on maintaining your commercial space's most valuable assets—from MEP systems to everyday cleanliness.",
                    "eyebrow": "Facility Management",
                },
                ["title", "hero_headline", "hero_subcopy", "eyebrow"],
            )
            print(f" {'[~] Updated' if changed else '[=] Kept   '} Service")
        else:
            print(" [dry] Would update Service metadata")

        # Metrics
        METRICS = [
            {"value": "< 2 Hours", "label": "Emergency Response Time", "sort_order": 1},
            {"value": "98%", "label": "Systems Uptime", "sort_order": 2},
            {"value": "500+", "label": "Properties Under Management", "sort_order": 3},
            {"value": "24/7", "label": "Support Availability", "sort_order": 4},
        ]
        for m in METRICS:
            if args.dry_run:
                print(f" [dry] Would seed Metric • {m['label']}")
            else:
                obj, _ = ServiceMetric.objects.get_or_create(service=svc, label=m["label"])
                changed = upsert(obj, m, ["value", "label", "sort_order"])
                print(f" {'[~] Updated' if changed else '[=] Kept   '} Metric • {obj.label}")

        # Capabilities
        CAPABILITIES = [
            {
                "title": "Hard Services",
                "blurb": "MEP systems, HVAC, electrical, plumbing, fire safety, and structural maintenance.",
                "icon_class": "fa-solid fa-wrench",
                "sort_order": 1,
            },
            {
                "title": "Soft Services",
                "blurb": "Cleaning, waste management, security, reception, pest control, and hygiene services.",
                "icon_class": "fa-solid fa-broom",
                "sort_order": 2,
            },
            {
                "title": "Pool & Landscape Maintenance",
                "blurb": "Chemical balancing, filtration, equipment servicing, irrigation, and seasonal planting.",
                "icon_class": "fa-solid fa-water",
                "sort_order": 3,
            },
            {
                "title": "Emergency Response",
                "blurb": "24/7 rapid deployment for critical issues, system failures, and urgent repairs.",
                "icon_class": "fa-solid fa-clock",
                "sort_order": 4,
            },
            {
                "title": "Preventive Maintenance",
                "blurb": "Scheduled inspections, testing, and servicing to prevent costly breakdowns.",
                "icon_class": "fa-solid fa-clipboard-check",
                "sort_order": 5,
            },
            {
                "title": "Quality & Reporting",
                "blurb": "Digital checklists, photo documentation, and performance metrics for transparency.",
                "icon_class": "fa-solid fa-chart-line",
                "sort_order": 6,
            },
        ]
        for c in CAPABILITIES:
            if args.dry_run:
                print(f" [dry] Would seed Capability • {c['title']}")
            else:
                obj, _ = ServiceCapability.objects.get_or_create(service=svc, title=c["title"])
                changed = upsert(obj, c, ["title", "blurb", "icon_class", "sort_order"])
                print(f" {'[~] Updated' if changed else '[=] Kept   '} Capability • {obj.title}")

        # Process Steps
        STEPS = [
            {"step_no": 1, "title": "Site Assessment", "description": "Comprehensive audit of systems, staffing needs, and service frequency requirements."},
            {"step_no": 2, "title": "Custom Plan", "description": "Tailored maintenance schedule, SLA definition, and cost breakdown with transparent pricing."},
            {"step_no": 3, "title": "Scheduled Service", "description": "Trained teams execute daily, weekly, and monthly tasks with minimal disruption."},
            {"step_no": 4, "title": "Quality Checks", "description": "Supervisors conduct inspections, photo documentation, and performance reviews."},
            {"step_no": 5, "title": "Reporting & Optimization", "description": "Monthly reports, service logs, and continuous improvement recommendations."},
        ]
        for s in STEPS:
            if args.dry_run:
                print(f" [dry] Would seed Process Step {s['step_no']}")
            else:
                obj, _ = ServiceProcessStep.objects.get_or_create(service=svc, step_no=s["step_no"])
                changed = upsert(obj, s, ["step_no", "title", "description"])
                print(f" {'[~] Updated' if changed else '[=] Kept   '} Process Step {obj.step_no}")

        # FAQs
        FAQS = [
            {"question": "What's included in your facility management services?", "answer": "We provide comprehensive hard services (MEP, HVAC, electrical, plumbing, fire safety) and soft services (cleaning, waste management, security, pest control). Pool and landscape maintenance are also available as add-ons or standalone services.", "sort_order": 1},
            {"question": "How quickly do you respond to emergencies?", "answer": "Our 24/7 emergency response team deploys within 2 hours for critical issues like MEP failures, flooding, electrical outages, or safety hazards. We maintain standby crews and stock commonly needed parts to minimize downtime.", "sort_order": 2},
            {"question": "Do you handle permits and compliance inspections?", "answer": "Yes. We coordinate civil defense inspections, health & safety audits, and authority compliance. Our team prepares documentation, schedules visits, and ensures your facility meets all regulatory requirements.", "sort_order": 3},
            {"question": "Can I customize the service frequency?", "answer": "Absolutely. We tailor schedules to your needs—daily cleaning, weekly HVAC checks, monthly pool servicing, or quarterly deep maintenance. You only pay for what you need.", "sort_order": 4},
            {"question": "How do you ensure quality and accountability?", "answer": "Every service includes digital checklists, photo documentation, and timestamped logs. Supervisors conduct quality inspections, and you receive monthly performance reports with metrics, issues resolved, and improvement recommendations.", "sort_order": 5},
            {"question": "What happens if a technician is unavailable?", "answer": "We maintain backup staffing and cross-train teams to ensure continuity. If a scheduled technician is unavailable, a qualified replacement is deployed. For specialized tasks (e.g., pool chemistry), we have certified alternates on standby.", "sort_order": 6},
        ]
        for faq in FAQS:
            if args.dry_run:
                print(f" [dry] Would seed FAQ • {faq['question'][:50]}...")
            else:
                obj, _ = ServiceFAQ.objects.get_or_create(service=svc, question=faq["question"])
                changed = upsert(obj, faq, ["question", "answer", "sort_order"])
                print(f" {'[~] Updated' if changed else '[=] Kept   '} FAQ • {obj.question[:50]}...")

        # Service Showcases with distributed images
        for meta, showcase_images in distributed:
            print(f"\n--- {meta['title']} ---")
            print(f"    Assigned {len(showcase_images)} images")

            if not showcase_images:
                print("    [!] No images assigned, skipping")
                continue

            # Use first image as hero
            hero_src = showcase_images[0]
            public_base = f"{slugify(meta['title'])}/{file_md5(hero_src)}"

            if args.dry_run:
                print(f" [dry] HERO would upload: {hero_src.name} → {public_base}")
                base_hero_url = f"(dry-run)/{public_base}.jpg"
            else:
                data, ext = load_and_precompress(hero_src)
                resp = cloudinary_upload(data, public_id=public_base, folder=args.cloud_folder)
                base_hero_url = resp["secure_url"]

            hero_full_url = cloudinary_variant(base_hero_url, width=1600, height=900)
            hero_thumb_url = cloudinary_variant(base_hero_url, width=800, height=450)

            # Create/update CaseStudy
            if not args.dry_run:
                cs_obj, _ = CaseStudy.objects.get_or_create(service=svc, title=meta["title"])
                changed = upsert(
                    cs_obj,
                    {
                        "hero_image_url": hero_full_url,
                        "thumb_url": hero_thumb_url,
                        "full_url": hero_full_url,
                        "summary": meta["summary"],
                        "description": meta["description"],
                        "completion_date": date.today(),
                        "scope": "Service Offering",
                        "size_label": "—",
                        "timeline_label": "Ongoing",
                        "status_label": "Active",
                        "tags_csv": meta["tags_csv"],
                        "is_featured": meta["is_featured"],
                        "sort_order": meta["sort_order"],
                        "cta_url": "",
                        "location": "Dubai, UAE",
                        "project_type": "facility-management",
                    },
                    [
                        "hero_image_url", "thumb_url", "full_url", "summary", "description",
                        "completion_date", "scope", "size_label", "timeline_label", "status_label",
                        "tags_csv", "is_featured", "sort_order", "cta_url", "location", "project_type",
                    ],
                )
                print(f" {'[~] Updated' if changed else '[=] Kept   '} Showcase • {cs_obj.title}")
            else:
                print(f" [dry] Would create/update Showcase • {meta['title']}")

            # Build gallery
            gallery_items = []
            for g_i, img_path in enumerate(showcase_images, start=1):
                public_img = f"{slugify(meta['title'])}/{file_md5(img_path)}"
                if args.dry_run:
                    print(f" [dry] GALLERY would upload: {img_path.name} → {public_img}")
                    base_url = f"(dry-run)/{public_img}.jpg"
                else:
                    data, ext = load_and_precompress(img_path)
                    resp = cloudinary_upload(data, public_id=public_img, folder=args.cloud_folder)
                    base_url = resp["secure_url"]

                thumb_url = cloudinary_variant(base_url, width=800, height=450)
                full_url = cloudinary_variant(base_url, width=1600, height=900)

                gallery_items.append({
                    "thumb": thumb_url,
                    "full": full_url,
                    "caption": f"{meta['title']} — View {g_i}",
                })

            # Save gallery to JSONField
            if not args.dry_run:
                cs_obj.gallery_urls = gallery_items
                cs_obj.save()

            print(f"     ↳ {'(dry-run) ' if args.dry_run else ''}Seeded {len(showcase_images)} gallery images")

    print("\n[✓] Done seeding Facility Management & Aftercare.")


if __name__ == "__main__":
    main()

