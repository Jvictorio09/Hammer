# myApp/utils/cloudinary_utils.py
import io
from pathlib import Path
from PIL import Image, ImageOps
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError

MAX_BYTES = 10 * 1024 * 1024
TARGET_BYTES = int(MAX_BYTES * 0.93)

def smart_compress_to_bytes(src_file) -> bytes:
    """
    Accepts a file-like or path; returns bytes <= TARGET_BYTES.
    """
    # Load into Pillow
    if isinstance(src_file, (str, Path)):
        im = Image.open(src_file)
    else:
        im = Image.open(src_file)

    with im:
        im = ImageOps.exif_transpose(im)
        fmt = (im.format or "JPEG").upper()
        prefer_webp = fmt in ("PNG", "TIFF")
        out_fmt = "WEBP" if prefer_webp else ("JPEG" if fmt != "WEBP" else "WEBP")

        # Cap extremes
        max_w = 5000
        if im.width > max_w:
            im = im.resize((max_w, int(im.height * (max_w / im.width))), Image.LANCZOS)

        q = 82
        min_q = 50 if out_fmt == "JPEG" else 45
        step  = 4
        while True:
            buf = io.BytesIO()
            if out_fmt == "JPEG":
                im.save(buf, format="JPEG", quality=q, optimize=True, progressive=True, subsampling="4:2:0")
            else:
                im.save(buf, format="WEBP", quality=q, method=6)
            data = buf.getvalue()
            if len(data) <= TARGET_BYTES or q <= min_q:
                return data
            q = max(min_q, q - step)

def upload_to_cloudinary(file_bytes: bytes, folder: str, public_id: str, tags=None):
    """Signed upload; returns Cloudinary response and 3 helpful URLs."""
    result = cloudinary.uploader.upload(
        file=io.BytesIO(file_bytes),
        resource_type="image",
        folder=folder or "uploads",
        public_id=public_id,
        overwrite=True,
        unique_filename=False,
        use_filename=False,
        eager=[{"format":"webp","quality":"auto","fetch_format":"auto","crop":"limit","width":2400}],
        tags=(tags or []),
        timeout=120,
    )
    secure_url = result.get("secure_url", "")
    web_url = secure_url.replace("/upload/", "/upload/f_auto,q_auto/") if "/upload/" in secure_url else secure_url
    thumb_url = secure_url.replace("/upload/", "/upload/c_fill,g_face,w_480,h_320/") if "/upload/" in secure_url else secure_url
    return result, web_url, thumb_url
