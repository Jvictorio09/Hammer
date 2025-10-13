#!/usr/bin/env python3
"""
Seed Case Studies for 'Landscape Design & Build' from local folders → Cloudinary → DB.

Usage (examples):

  # Default: metadata-only mode (no file scan, no image uploads, sources from TARGETS)
  python seed_landscape.py --settings myProject.settings ^
    --service-slug landscape-design-build

  # Dry-run metadata updates
  python seed_landscape.py --settings myProject.settings ^
    --service-slug landscape-design-build ^
    --dry-run

  # Enable image uploads/variants/gallery (opt-in)
  python seed_landscape.py --settings myProject.settings ^
    --service-slug landscape-design-build ^
    --root "E:\\New Downloads\\Hammer\\Landscape" ^
    --cloud-folder hammer/landscape ^
    --images

  # Filter to specific projects only (metadata mode)
  python seed_landscape.py --settings myProject.settings ^
    --service-slug landscape-design-build ^
    --only "tilal al ghaf,jumeirah park"

  # Wipe and re-seed with images
  python seed_landscape.py --settings myProject.settings ^
    --service-slug landscape-design-build ^
    --root "E:\\New Downloads\\Hammer\\Landscape" ^
    --cloud-folder hammer/landscape ^
    --images ^
    --wipe

Notes:
- Idempotent: existing Case Studies update instead of duplicating.
- Only seeds folders: Tilal Al Ghaf, Murooj, Jumeirah Park (typo 'Jumeriah park' tolerated).
- By default (--no-images), only metadata is updated; image URLs are preserved. No --root needed.
- In metadata-only mode, projects are sourced from TARGETS dict (no filesystem scan).
- Use --images to enable image uploads, recompression, and gallery generation (requires --root).
- Use --only to filter specific projects (comma-separated normalized folder keys).
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
# Django bootstrap (mirror your style)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

parser = argparse.ArgumentParser(description="Seed Landscape Case Studies from folders")
parser.add_argument("--settings", help="Django settings module (e.g., myProject.settings)")
parser.add_argument("--service-id", type=int, help="Service ID to attach case studies to")
parser.add_argument("--service-slug", help="Service slug to attach case studies to")
parser.add_argument("--service-title", help="Service title (fallback if id/slug missing)")
parser.add_argument("--root", help=r'Root folder, e.g. "E:\New Downloads\Hammer\Landscape" (required for --images mode)')
parser.add_argument("--cloud-folder", default="hammer/landscape", help="Cloudinary folder prefix")
parser.add_argument("--wipe", action="store_true", help="Delete existing Case Studies for this service first")
parser.add_argument("--dry-run", action="store_true", help="Print actions; no uploads, no DB writes")
parser.add_argument("--only", help="Comma-separated list of normalized folder keys to process (e.g., 'tilal al ghaf,jumeirah park')")

# Mutually exclusive image mode flags
mx = parser.add_mutually_exclusive_group()
mx.add_argument("--no-images", dest="no_images", action="store_true", help="Do not touch image fields (default).")
mx.add_argument("--images", dest="no_images", action="store_false", help="Enable image upload + gallery.")
parser.set_defaults(no_images=True)

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

# Gallery is stored in CaseStudy.gallery_urls as JSONField (no separate model needed)

# -----------------------------------------------------------------------------
# Config / Targets
# -----------------------------------------------------------------------------
# Lowercased keys for robust matching.
TARGETS = {
    "tilal al ghaf": {
        "title": "Tilal Al Ghaf",
        "summary": "A modern oasis in the heart of the city, featuring a private courtyard pool framed by elegant cactus arrangements and olive trees.",
        "description": "A modern oasis in the heart of the city, the Tilal Al Ghaf landscape project features a private courtyard pool framed by elegant cactus arrangements and olive trees. Subtle lighting highlights the textures of natural elements, creating a warm, inviting atmosphere perfect for relaxing evenings and intimate gatherings.",
        "completion_date": date(2025, 6, 27),
        "location": "Dubai",
        "is_featured": True,
    },
    "murooj": {
        "title": "Murooj Al Furjan",
        "summary": "Luxury landscape design in Dubai with a modern pool, pergola, and lush greenery.",
        "description": "Luxury landscape design in Dubai with a modern pool, pergola, and lush greenery. Created by Hammer Landscape & Pools for stylish outdoor living.",
        "completion_date": date(2025, 9, 3),
        "location": "Dubai, UAE",
        "is_featured": False,
    },
    "jumeirah park": {
        "title": "Jumeirah Park",
        "summary": "Family-friendly landscape with clean hardscape, night lighting, and resilient planting.",
        "description": "A thoughtfully designed outdoor space featuring clean hardscape, strategic night lighting, and climate-resilient planting. Perfect for family living and entertaining in Dubai's environment.",
        "completion_date": date(2025, 9, 4),
        "location": "Dubai, UAE",
        "is_featured": False,
    },
}

# Common misspellings/variations (left side will be normalized to the right).
TARGET_ALIASES = {
    "jumeriah park": "jumeirah park",
}

# -----------------------------------------------------------------------------
# Field Constants
# -----------------------------------------------------------------------------
METADATA_FIELDS = [
    "summary", "description", "completion_date", "scope", "size_label", "timeline_label",
    "status_label", "tags_csv", "is_featured", "sort_order", "cta_url", "location", "project_type",
]
IMAGE_FIELDS = ["hero_image_url", "thumb_url", "full_url"]
GALLERY_FIELD = "gallery_urls"

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

    # Validate credentials early, fail fast
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

    # Configure (CLOUDINARY_URL or discrete envs)
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    full_public_id = f"{folder}/{public_id}" if folder else public_id

    # Upload original (already pre-compressed). Delivery transforms are added via URL (no re-uploads).
    resp = cloudinary.uploader.upload(
        io.BytesIO(data_bytes),
        public_id=full_public_id,
        overwrite=overwrite,
        resource_type="image",
        use_filename=True,
        unique_filename=False,
        folder=folder or None,
        quality="auto:good",  # delivery optimization
        format="jpg",         # canonicalize photos to jpg
    )
    return resp


def cloudinary_variant(base_url: str, width: int, height: int, crop="fill", gravity="auto") -> str:
    """
    Build a **delivery URL** by injecting a Cloudinary transformation (no re-upload).
    Example: adds /c_fill,g_auto,w_<w>,h_<h>,f_auto,q_auto:good after /upload/.
    """
    if "/upload/" not in base_url:
        return base_url
    trans = f"c_{crop},g_{gravity},w_{width},h_{height},f_auto,q_auto:good"
    return base_url.replace("/upload/", f"/upload/{trans}/", 1)


def projects_from_targets(only_filter=None):
    """
    Build a projects list straight from TARGETS (no filesystem).
    Returns list of (folder_name, project_config, folder_path, image_paths[])
    
    Args:
        only_filter: Optional set of normalized folder keys to include
    """
    items = []
    for key, cfg in TARGETS.items():
        if only_filter and key not in only_filter:
            continue
        # Use title as folder_name placeholder; no path/images in metadata mode
        items.append((cfg["title"], cfg, None, []))
    return items


def discover_projects(root: Path, only_filter=None):
    """
    Scan root for target subfolders and RECURSIVELY find all image files (including subfolders).
    Returns list of (folder_name, project_config, folder_path, image_paths[])
    
    Args:
        root: Root directory to scan
        only_filter: Optional set of normalized folder keys to include (e.g., {"tilal al ghaf", "jumeirah park"})
    """
    found = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        key_lower = _normalize_folder_key(child.name)
        
        # Skip if not in filter (when filter is provided)
        if only_filter and key_lower not in only_filter:
            continue
            
        if key_lower in TARGETS:
            config = TARGETS[key_lower]
            imgs: List[Path] = []
            # Use rglob to recursively find images in ALL subfolders
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.JPEG", "*.PNG", "*.WEBP"):
                imgs.extend(sorted(child.rglob(ext)))
            # Always include the project; images may be empty if you're just organizing now
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
def seed_landscape(service: Service, root: Optional[Path], cloud_folder: str, dry_run: bool, wipe: bool, no_images: bool, only_filter=None):
    # Only validate image deps when needed
    if not no_images:
        ensure_pillow()
        ensure_cloudinary()

    # Build the project list
    if no_images:
        # In metadata-only mode, we don't need the filesystem at all
        projects = projects_from_targets(only_filter=only_filter)
        if not projects:
            print("[!] No matching TARGETS to process.")
            return 0, 0, 0
        print("[info] --no-images mode: sourcing projects from TARGETS (no file scan).")
    else:
        if not root or not root.exists():
            raise FileNotFoundError(f"Root folder not found: {root}")
        projects = discover_projects(root, only_filter=only_filter)
        if not projects:
            print(f"[!] No target projects found under: {root}")
            return 0, 0, 0

    print(f"[i] Seeding Case Studies for Service: {getattr(service, 'title', service.id)}")
    print(f"[i] Found {len(projects)} project folder(s): {', '.join([p[0] for p in projects])}")

    if wipe:
        print("[!] Wiping existing Case Studies for this service…")
        service.case_studies.all().delete()

    created_count = 0
    updated_count = 0

    for idx, (folder_name, config, folder_path, image_paths) in enumerate(projects, start=1):
        title = config["title"]
        summary = config["summary"]
        description = config["description"]
        completion_date = config["completion_date"]
        location = config["location"]
        is_featured = config["is_featured"]
        
        print(f"\n--- {title}  ({folder_name}) ---")
        print(f"    Found {len(image_paths)} images (including subfolders)")

        # Prepare metadata dict (always included)
        metadata_dict = {
            "summary": summary,
            "description": description,
            "completion_date": completion_date,
            "scope": "Design + Build",
            "size_label": "—",
            "timeline_label": "—",
            "status_label": "Completed",
            "tags_csv": "Landscape, Pool, Lighting",
            "is_featured": is_featured,
            "sort_order": idx,
            "cta_url": "",
            "location": location,
            "project_type": "landscape",
        }

        # Handle images if enabled
        if no_images:
            print(f" [-img-] Skipping hero/thumb/full and gallery; preserving existing URLs.")
            fields_to_update = METADATA_FIELDS
            update_dict = metadata_dict
        else:
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

            # Add image fields to update dict
            update_dict = {
                **metadata_dict,
                "hero_image_url": hero_full_url,
                "thumb_url": hero_thumb_url,
                "full_url": hero_full_url,
            }
            fields_to_update = METADATA_FIELDS + IMAGE_FIELDS

        # Upsert Case Study
        cs_obj, created = CaseStudy.objects.get_or_create(service=service, title=title)
        
        if created:
            created_count += 1
            if no_images and not dry_run:
                # Warn if creating new case study without images
                print(f" [warn] New Case Study created; hero/thumb/full remain empty in --no-images mode.")
        
        if dry_run:
            print(f" [dry]{'[skip-img] ' if no_images else ''} Would update fields: {', '.join(fields_to_update)}")
            changed = True
        else:
            changed = upsert(cs_obj, update_dict, fields_to_update)
        
        if not created:
            if changed:
                updated_count += 1
        
        print(f" {'[+] Created' if created else '[~] Updated' if changed else '[=] Kept   '} Case Study • {cs_obj.title}")

        # Gallery: build JSON array for gallery_urls field (only in images mode)
        if not no_images:
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
    
    return created_count, updated_count, len(projects)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Print mode banner
    mode_str = "OFF (metadata only)" if args.no_images else "ON (uploads + gallery)"
    print(f"[mode] images: {mode_str}")
    if args.dry_run:
        print("[mode] dry-run: ON (no DB writes, no uploads)")
    
    # Parse --only filter
    only_filter = None
    if args.only:
        # Normalize and create a set of folder keys
        raw_keys = [k.strip() for k in args.only.split(",")]
        only_filter = {_normalize_folder_key(k) for k in raw_keys if k.strip()}
        print(f"[filter] Only processing: {', '.join(sorted(only_filter))}")
    
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

    root_path = Path(args.root) if args.root else None
    try:
        created, updated, total = seed_landscape(
            service=svc,
            root=root_path,
            cloud_folder=args.cloud_folder,
            dry_run=args.dry_run,
            wipe=args.wipe,
            no_images=args.no_images,
            only_filter=only_filter,
        )
    except Exception as e:
        print(f"[!] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Summary
    print("\n" + "="*60)
    print("✔ Landscape Case Studies seed complete.")
    print(f"  Mode: images {mode_str}")
    print(f"  Projects processed: {total}")
    print(f"  Case studies created: {created}")
    print(f"  Case studies updated: {updated}")
    if args.dry_run:
        print(f"  (dry-run mode: no actual changes made)")
    print("="*60)
