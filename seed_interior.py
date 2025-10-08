#!/usr/bin/env python3
"""
Seed 'Interior Design & Fit-Out' Case Studies from local folders → Cloudinary → DB.

Usage:
  python seed_interior.py --settings myProject.settings ^
    --service-slug interior-design-fitout ^
    --root "E:\\New Downloads\\Hammer\\3D Render Interior" ^
    --cloud-folder hammer/interior ^
    --wipe

Notes:
- Idempotent: existing Case Studies update instead of duplicating.
- Discovers all subfolders and uploads images recursively.
- If --wipe is set, removes only Case Studies (+ gallery images) for the target service.
"""

import os
import sys
import io
import argparse
import hashlib
from datetime import date
from pathlib import Path
from typing import Optional, List, Tuple

# -----------------------------------------------------------------------------
# Django bootstrap
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Seed Interior Case Studies from folders")
parser.add_argument("--settings", help="Django settings module (e.g., myProject.settings)")
parser.add_argument("--service-id", type=int, help="Service ID to attach case studies to")
parser.add_argument("--service-slug", help="Service slug to attach case studies to")
parser.add_argument("--service-title", help="Service title (fallback if id/slug missing)")
parser.add_argument("--root", required=True, help=r'Root folder, e.g., "E:\New Downloads\Hammer\3D Render Interior"')
parser.add_argument("--cloud-folder", default="hammer/interior", help="Cloudinary folder prefix")
parser.add_argument("--wipe", action="store_true", help="Delete existing Case Studies for this service first")
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
    CaseStudy,
)

# -----------------------------------------------------------------------------
# Config / Targets
# -----------------------------------------------------------------------------
# Normalized folder names → metadata
TARGETS = {
    "greg- the villa": {
        "title": "The Villa — Contemporary Elegance",
        "summary": "Refined living spaces with minimalist lines, natural materials, and timeless finishes.",
        "description": "A modern villa interior where clean geometry meets warm materiality. Floor-to-ceiling apertures invite natural light across open-plan living zones, while bespoke joinery and neutral palettes create a backdrop for curated art and quiet luxury.",
        "completion_date": date(2025, 7, 15),
        "location": "Dubai, UAE",
        "is_featured": True,
    },
    "home office": {
        "title": "Executive Home Office",
        "summary": "Sophisticated workspace blending productivity with residential comfort.",
        "description": "A tailored home office designed for focus and creativity. Custom millwork, task lighting, and ergonomic planning meet residential warmth—paneling, layered textures, and considered acoustics for video calls and deep work.",
        "completion_date": date(2025, 8, 10),
        "location": "Dubai, UAE",
        "is_featured": False,
    },
    "jordan apartment": {
        "title": "Jordan Residence",
        "summary": "Contemporary apartment with flowing spaces and residential intimacy.",
        "description": "A modern apartment balancing openness with privacy. Circulation flows between living, dining, and private quarters through subtle threshold moments. Material choices—soft stone, warm timber, linen textiles—echo the comfort of home.",
        "completion_date": date(2025, 6, 20),
        "location": "Amman, Jordan",
        "is_featured": True,
    },
    "jumeira park": {
        "title": "Jumeirah Park Family Villa",
        "summary": "Family-friendly interiors with durable finishes and flexible zoning.",
        "description": "A villa interior designed for everyday family life. Durable surfaces, smart storage, and flexible furniture layouts accommodate play, study, and entertaining. Neutral foundations allow personality to evolve over time.",
        "completion_date": date(2025, 9, 5),
        "location": "Dubai, UAE",
        "is_featured": False,
    },
    "random int. render": {
        "title": "Signature Interiors Collection",
        "summary": "Curated interior moments showcasing diverse spatial typologies and material vocabularies.",
        "description": "A collection of interior vignettes—foyers, dining rooms, family living—each exploring different aesthetic directions. From formal to casual, these spaces demonstrate versatility in planning, materiality, and lighting design.",
        "completion_date": date(2025, 8, 25),
        "location": "Dubai, UAE",
        "is_featured": False,
    },
}

# Common variations
TARGET_ALIASES = {
    "jumeirah park": "jumeira park",
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _normalize_folder_key(name: str) -> str:
    key = name.strip().lower()
    key = TARGET_ALIASES.get(key, key)
    return key


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


def load_and_precompress(path: Path, max_side=1920, jpeg_q=82, max_file_size=8*1024*1024) -> Tuple[bytes, str]:
    """
    Open image; downscale if oversized; encode to JPEG with quality adjustment to stay under size limit.
    Returns (bytes, 'jpg'|'png').
    """
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
    """
    Build a **delivery URL** by injecting a Cloudinary transformation (no re-upload).
    """
    if "/upload/" not in base_url:
        return base_url
    trans = f"c_{crop},g_{gravity},w_{width},h_{height},f_auto,q_auto:good"
    return base_url.replace("/upload/", f"/upload/{trans}/", 1)


def discover_projects(root: Path):
    """
    Scan root for target subfolders and RECURSIVELY find all image files.
    Returns list of (folder_name, project_config, folder_path, image_paths[])
    """
    found = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        key_lower = _normalize_folder_key(child.name)
        if key_lower in TARGETS:
            config = TARGETS[key_lower]
            imgs: List[Path] = []
            # Use rglob to recursively find images in ALL subfolders
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.JPEG", "*.PNG", "*.WEBP"):
                imgs.extend(sorted(child.rglob(ext)))
            if imgs:
                found.append((child.name, config, child, imgs))
    return found


def upsert(instance, data: dict, fields: List[str]) -> bool:
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
# Seeder
# -----------------------------------------------------------------------------
@transaction.atomic
def seed_interior(service: Service, root: Path, cloud_folder: str, dry_run: bool, wipe: bool):
    ensure_pillow()
    ensure_cloudinary()

    if not root.exists():
        raise FileNotFoundError(f"Root folder not found: {root}")

    projects = discover_projects(root)
    if not projects:
        print(f"[!] No target projects found under: {root}")
        return

    print(f"[i] Seeding Case Studies for Service: {getattr(service, 'title', service.id)}")
    print(f"[i] Found {len(projects)} project folder(s): {', '.join([p[0] for p in projects])}")

    if wipe:
        print("[!] Wiping existing Case Studies for this service…")
        service.case_studies.all().delete()

    for idx, (folder_name, config, folder_path, image_paths) in enumerate(projects, start=1):
        title = config["title"]
        summary = config["summary"]
        description = config["description"]
        completion_date = config["completion_date"]
        location = config["location"]
        is_featured = config["is_featured"]

        print(f"\n--- {title}  ({folder_name}) ---")
        print(f"    Found {len(image_paths)} images (including subfolders)")

        # Choose first image as hero
        hero_src = image_paths[0]

        # Upload hero (or simulate)
        public_base = f"{slugify(title)}/{file_md5(hero_src)}"
        if dry_run:
            print(f" [dry] HERO would upload: {hero_src} → public_id={public_base}")
            base_hero_url = f"(dry-run)/{public_base}.jpg"
        else:
            data, ext = load_and_precompress(hero_src)
            resp = cloudinary_upload(data, public_id=public_base, folder=cloud_folder)
            base_hero_url = resp["secure_url"]

        # Delivery variants (16:9 for consistency)
        hero_full_url = cloudinary_variant(base_hero_url, width=1600, height=900)
        hero_thumb_url = cloudinary_variant(base_hero_url, width=800, height=450)

        # Upsert Case Study
        if not dry_run:
            cs_obj, _ = CaseStudy.objects.get_or_create(service=service, title=title)
            changed = upsert(
                cs_obj,
                {
                    "hero_image_url": hero_full_url,
                    "thumb_url": hero_thumb_url,
                    "full_url": hero_full_url,
                    "summary": summary,
                    "description": description,
                    "completion_date": completion_date,
                    "scope": "Design + Fit-Out",
                    "size_label": "—",
                    "timeline_label": "—",
                    "status_label": "Completed",
                    "tags_csv": "Interior, Design, Fit-Out, 3D Render",
                    "is_featured": is_featured,
                    "sort_order": idx,
                    "cta_url": "",
                    "location": location,
                    "project_type": "interior",
                },
                [
                    "hero_image_url","thumb_url","full_url","summary","description",
                    "completion_date","scope","size_label","timeline_label","status_label",
                    "tags_csv","is_featured","sort_order","cta_url","location","project_type",
                ],
            )
            print(f" {'[~] Updated' if changed else '[=] Kept   '} Case Study • {cs_obj.title}")
        else:
            print(f" [dry] Would create/update Case Study • {title}")

        # Gallery: build JSON array for gallery_urls field
        gallery_items = []
        for g_i, img_path in enumerate(image_paths, start=1):
            public_img = f"{slugify(title)}/{file_md5(img_path)}"
            if dry_run:
                print(f" [dry] GALLERY would upload: {img_path.name} → {public_img}")
                base_url = f"(dry-run)/{public_img}.jpg"
            else:
                data, ext = load_and_precompress(img_path)
                resp = cloudinary_upload(data, public_id=public_img, folder=cloud_folder)
                base_url = resp["secure_url"]

            thumb_url = cloudinary_variant(base_url, width=800, height=450)
            full_url = cloudinary_variant(base_url, width=1600, height=900)

            gallery_items.append({
                "thumb": thumb_url,
                "full": full_url,
                "caption": f"{title} — View {g_i}",
            })

        # Save gallery to JSONField
        if not dry_run:
            cs_obj.gallery_urls = gallery_items
            cs_obj.save()

        print(f"     ↳ {'(dry-run) ' if dry_run else ''}Seeded {len(image_paths)} gallery images to gallery_urls")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Resolve Service
    svc: Optional[Service] = None
    if args.service_id:
        svc = Service.objects.filter(id=args.service_id).first()
    elif args.service_slug:
        svc = Service.objects.filter(slug=args.service_slug).first()
    elif args.service_title:
        svc = Service.objects.filter(title__iexact=args.service_title).first()
    else:
        svc = Service.objects.order_by("id").first()

    if not svc:
        print("[!] No Service found. Provide --service-id or --service-slug or --service-title.")
        sys.exit(1)

    root_path = Path(args.root)
    try:
        seed_interior(
            service=svc,
            root=root_path,
            cloud_folder=args.cloud_folder,
            dry_run=args.dry_run,
            wipe=args.wipe,
        )
    except Exception as e:
        print(f"[!] Seeding failed: {e}")
        sys.exit(1)

    print("\n✔ Interior Case Studies seed complete.")

