import os, sys, re, io, unicodedata
from pathlib import Path
from typing import Tuple

# ── Django bootstrap ──────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yourproject.settings")  # TODO: ← replace with your project (e.g., "myProject.settings")
import django
django.setup()

from django.conf import settings
from myApp.models import TeamMember  # TODO: ← adjust app label if different

# Cloudinary & Pillow
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudError
from PIL import Image

# ── Config ───────────────────────────────────────────────────
# 10MB Cloudinary free/unsigned limit. We'll compress a bit below it and retry.
TEN_MB = 10 * 1024 * 1024
TARGET_KB = 9500  # ~9.5MB

DASH_SPLIT = re.compile(r"\s*[-–—]\s*")  # hyphen / en-dash / em-dash


# ── Helpers ──────────────────────────────────────────────────
def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip()

def parse_name_role(stem: str) -> Tuple[str, str]:
    # "Aamra Khalid - Design Manager" -> ("Aamra Khalid", "Design Manager")
    stem = _normalize(stem)
    parts = DASH_SPLIT.split(stem, maxsplit=1)
    name = parts[0].strip()
    role = parts[1].strip() if len(parts) > 1 else ""
    return name, role

def public_id_for(name: str) -> str:
    # Stable slug; keep everything under "team/"
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not slug:
        slug = "member"
    return f"team/{slug}"

def configure_cloudinary():
    url = getattr(settings, "CLOUDINARY_URL", None) or os.getenv("CLOUDINARY_URL")
    if url:
        cloudinary.config(cloudinary_url=url, secure=True)
        return
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

def compress_to_target(path: str, target_kb: int = TARGET_KB) -> io.BytesIO:
    """
    Compress to JPEG ~target_kb (best effort) without changing aspect ratio.
    Always converts to RGB JPEG to keep things predictable.
    """
    img = Image.open(path)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    else:
        img = img.convert("RGB")

    buf = io.BytesIO()
    quality = 95
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    while (buf.tell() / 1024.0) > target_kb and quality > 60:
        quality -= 5
        buf.seek(0)
        buf.truncate()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
    buf.seek(0)
    return buf

def upload_with_retry(local_path: str, public_id: str) -> str:
    """
    Try signed upload. If Cloudinary complains about file size (>10MB),
    compress and retry automatically.
    Returns secure_url.
    """
    # Always do signed uploads (we have API secret); sign_url affects URL signing,
    # but providing credentials makes this a signed API call.
    try:
        res = cloudinary.uploader.upload(
            local_path,
            folder="team/",
            public_id=public_id,
            overwrite=True,
            use_filename=True,
            unique_filename=False,
            invalidate=True,
        )
        return res["secure_url"]
    except CloudError as e:
        msg = str(e)
        too_large = "File size too large" in msg or "Maximum is" in msg
        if too_large:
            # Compress then retry
            comp = compress_to_target(local_path, TARGET_KB)
            res = cloudinary.uploader.upload(
                comp,
                folder="team/",
                public_id=public_id,
                overwrite=True,
                use_filename=True,
                unique_filename=False,
                invalidate=True,
                resource_type="image",
            )
            return res["secure_url"]
        raise  # bubble up other errors

def seed_team(folder: str):
    p = Path(folder)
    if not p.exists():
        print(f"❌ Folder not found: {folder}")
        sys.exit(1)

    configure_cloudinary()
    print(f"📤 Uploading images from: {folder}\n")

    count = 0
    for order, filename in enumerate(sorted(os.listdir(folder)), start=1):
        lower = filename.lower()
        if not lower.endswith((".jpg", ".jpeg", ".png")):
            continue

        stem = os.path.splitext(filename)[0]
        name, role = parse_name_role(stem)
        local_path = str(p / filename)
        public_id = public_id_for(name)

        # If local file >10MB, we’ll still try original first (maybe plan allows it),
        # then auto-compress and retry if Cloudinary rejects.
        try:
            url = upload_with_retry(local_path, public_id)
        except CloudError as e:
            print(f"❌ {filename} → Cloudinary error: {e}")
            continue

        TeamMember.objects.update_or_create(
            name=name,
            defaults={
                "role": role,
                "photo_url": url,
                "is_active": True,
                "is_featured": True,
                "sort_order": order,
            },
        )
        print(f"✅ {name} ({role}) → {url}")
        count += 1

    total = TeamMember.objects.count()
    print(f"\n🎉 Done! Uploaded/updated {count} item(s). Team total in DB: {total}")

if __name__ == "__main__":
    FOLDER = r"E:\New Downloads\TEAM PICTURES - WEBSITE ONLY-20251006T114802Z-1-001\TEAM PICTURES - WEBSITE ONLY"
    seed_team(FOLDER)
