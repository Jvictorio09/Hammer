# docs.py
# Run from the project root (same folder as manage.py)
# Usage: python docs.py [optional_path]
# If no path is provided, it uses the FOLDER constant below.

import os
import sys
import io
import math
from pathlib import Path
from datetime import datetime

# Pillow for compression
from PIL import Image, ImageOps

# Cloudinary
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError

# Optionally read Django settings (to get env or CLOUDINARY_* from settings)
import django
from django.conf import settings

# ------------- CONFIG -------------
# Default folder if not passed as argv[1]
FOLDER = r"E:\New Downloads\DUABI HILLS, PARKWAYS-20251006T132835Z-1-001\DUABI HILLS, PARKWAYS"

# Hard limit for Cloudinary free/standard plans: 10 MB
# We'll aim a little under to be safe.
MAX_BYTES = 10 * 1024 * 1024        # 10,485,760
TARGET_BYTES = int(MAX_BYTES * 0.93) # ~9.7 MB

# Default Cloudinary folder prefix for projects
CLOUD_FOLDER_PREFIX = "projects"

# Eager transformation (optional): generate a web-ready variant you can use
# You can comment this out if you don't need eager transforms.
EAGER_TRANSFORMS = [
    {"format": "webp", "quality": "auto", "fetch_format": "auto", "crop": "limit", "width": 2400}
]

# ------------- HELPERS -------------

def setup_django_settings():
    """
    Initialize Django so we can read settings/ENV if needed.
    """
    # Find manage.py directory and add to path
    root = Path(__file__).resolve().parent
    sys.path.append(str(root))
    # Try to find settings module from manage.py context
    # If your DJANGO_SETTINGS_MODULE is already set, this is a no-op
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
    try:
        django.setup()
    except Exception:
        # If setup fails, we'll still rely on env variables directly.
        pass

def configure_cloudinary_from_settings_or_env():
    """
    Configure Cloudinary using (in order):
      1) Django settings CLOUDINARY_URL or CLOUDINARY dict,
      2) Environment variables (CLOUDINARY_URL or cloud_name/api_key/api_secret).
    """
    # 1) From Django settings
    url = getattr(settings, "CLOUDINARY_URL", None)
    if url:
        cloudinary.config(cloudinary_url=url, secure=True)
        return

    cfg = getattr(settings, "CLOUDINARY", None)
    if isinstance(cfg, dict) and {"cloud_name","api_key","api_secret"} <= set(cfg.keys()):
        cloudinary.config(
            cloud_name=cfg["cloud_name"],
            api_key=cfg["api_key"],
            api_secret=cfg["api_secret"],
            secure=True
        )
        return

    # 2) From environment
    env_url = os.getenv("CLOUDINARY_URL")
    if env_url:
        cloudinary.config(cloudinary_url=env_url, secure=True)
        return

    cn = os.getenv("CLOUDINARY_CLOUD_NAME")
    ak = os.getenv("CLOUDINARY_API_KEY")
    sec = os.getenv("CLOUDINARY_API_SECRET")
    if cn and ak and sec:
        cloudinary.config(cloud_name=cn, api_key=ak, api_secret=sec, secure=True)
        return

    raise RuntimeError("Cloudinary credentials not found. Set CLOUDINARY_URL or cloud_name/api_key/api_secret.")

def human(n):
    for u in ["B","KB","MB","GB"]:
        if n < 1024.0:
            return f"{n:0.1f} {u}"
        n /= 1024.0
    return f"{n:0.1f} TB"

def is_image(path: Path) -> bool:
    return path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}

def sanitize_public_id(name: str) -> str:
    # Strip extension and make a tidy id
    base = Path(name).stem
    # Keep alnum, dash, underscore and forward slash (cloudinary rules)
    import re
    base = re.sub(r"[^a-zA-Z0-9_\-]+", "_", base).strip("_")
    # Lowercase for consistency
    return base[:120]

def smart_compress_to_bytes(src_path: Path, target_bytes: int) -> bytes:
    """
    Compress an image to <= target_bytes using Pillow.
    - Converts to JPEG for photographic content (or keeps WebP if already WebP).
    - Progressive + optimize.
    - Iteratively reduces quality if needed.
    Returns raw bytes ready to upload.
    """
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im)  # fix orientation
        fmt = im.format or "JPEG"
        # Prefer WebP for very large PNGs/JPEGs
        prefer_webp = fmt.upper() in ("PNG","TIFF") or src_path.suffix.lower() in (".png",".tif",".tiff")
        out_fmt = "WEBP" if prefer_webp else ("JPEG" if fmt.upper() != "WEBP" else "WEBP")

        # Start quality guess based on size: bigger file → lower start quality
        file_bytes = src_path.stat().st_size
        if file_bytes > 30*1024*1024:
            q = 65
        elif file_bytes > 15*1024*1024:
            q = 75
        else:
            q = 82

        min_q = 50 if out_fmt == "JPEG" else 45
        step  = 4

        # Optional: cap max dimensions to something reasonable (saves tons of bytes)
        # Remove or tweak to taste.
        max_w = 5000
        if im.width > max_w:
            new_h = int(im.height * (max_w / im.width))
            im = im.resize((max_w, new_h), Image.LANCZOS)

        while True:
            buf = io.BytesIO()
            save_kwargs = {}
            if out_fmt == "JPEG":
                save_kwargs = dict(format="JPEG", quality=q, optimize=True, progressive=True, subsampling="4:2:0")
            elif out_fmt == "WEBP":
                save_kwargs = dict(format="WEBP", quality=q, method=6)
            else:
                save_kwargs = dict(format="JPEG", quality=q, optimize=True, progressive=True)

            im.save(buf, **save_kwargs)
            data = buf.getvalue()
            if len(data) <= target_bytes or q <= min_q:
                return data
            q = max(min_q, q - step)

def ensure_under_limit(path: Path, target_bytes: int) -> tuple[bytes, str]:
    """
    If file is already under target, return disk bytes.
    Otherwise compress to <= target and return.
    Returns (bytes_data, extension_hint)
    """
    size = path.stat().st_size
    if size <= target_bytes:
        with open(path, "rb") as f:
            return f.read(), path.suffix.lower().strip(".") or "jpg"
    data = smart_compress_to_bytes(path, target_bytes)
    # Guess extension from bytes (we know what we saved in compressor)
    # We’ll peek first few bytes to decide; simple heuristic:
    ext = "webp" if data[:12].startswith(b"RIFF") else "jpg"
    return data, ext

def print_header(title):
    print("\n" + title)
    print("-" * len(title))

# ------------- MAIN -------------

def main():
    setup_django_settings()
    configure_cloudinary_from_settings_or_env()

    base_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(FOLDER)
    if not base_path.exists():
        raise SystemExit(f"Folder not found: {base_path}")

    # Cloudinary folder name: projects/<dir_name_slug>
    dir_name = base_path.name.strip().replace(" ", "_").lower()
    cld_folder = f"{CLOUD_FOLDER_PREFIX}/{dir_name}"

    print_header(f"📤 Uploading images from: {base_path}")
    print(f"Cloudinary folder: {cld_folder}")

    # Collect files
    files = [p for p in sorted(base_path.iterdir()) if p.is_file() and is_image(p)]
    if not files:
        print("No images found.")
        return

    successes = []
    failures  = []

    for p in files:
        try:
            original_size = p.stat().st_size
            data, ext_hint = ensure_under_limit(p, TARGET_BYTES)

            # Build public_id
            public_id = sanitize_public_id(p.stem)

            # Try upload (signed)
            try:
                result = cloudinary.uploader.upload(
                    file=io.BytesIO(data),
                    resource_type="image",
                    folder=cld_folder,
                    public_id=public_id,
                    overwrite=True,
                    unique_filename=False,
                    use_filename=False,
                    # eager transforms generate web versions eagerly (optional)
                    eager=EAGER_TRANSFORMS,
                    # tags to track
                    tags=["auto-upload", dir_name, "project"],
                    timeout=120,
                )
            except CloudinaryError as e:
                msg = str(e)
                # If still too large, apply another compression pass tighter and retry once
                if "File size too large" in msg or "Maximum is" in msg:
                    tighter = smart_compress_to_bytes(p, int(TARGET_BYTES*0.9))
                    result = cloudinary.uploader.upload(
                        file=io.BytesIO(tighter),
                        resource_type="image",
                        folder=cld_folder,
                        public_id=public_id,
                        overwrite=True,
                        unique_filename=False,
                        use_filename=False,
                        eager=EAGER_TRANSFORMS,
                        tags=["auto-upload", dir_name, "project", "retry"],
                        timeout=120,
                    )
                else:
                    raise

            # Delivery URL (with sane defaults)
            secure_url = result.get("secure_url", "")
            # Encourage browser to use auto format/quality (URL-based transform)
            # Only add if not already transformed
            if "/upload/" in secure_url and "/f_auto" not in secure_url:
                secure_url = secure_url.replace("/upload/", "/upload/f_auto,q_auto/")

            final_bytes = result.get("bytes", 0)
            print(f"✅ {p.name}  ({human(original_size)} → {human(final_bytes)})")
            print(f"    {secure_url}")
            successes.append((p.name, original_size, final_bytes, secure_url))
        except Exception as ex:
            print(f"❌ {p.name}  — {ex}")
            failures.append((p.name, str(ex)))

    # Summary
    print_header("Summary")
    for name, o, f, url in successes:
        print(f"• {name}: {human(o)} → {human(f)}")
        print(f"  {url}")
    if failures:
        print_header("Failures")
        for name, err in failures:
            print(f"• {name}: {err}")

    print("\nDone.\n")

if __name__ == "__main__":
    main()
