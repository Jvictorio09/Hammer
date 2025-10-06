# myApp/utils/cloudinary_uploads.py
import cloudinary.uploader

def upload_and_get_url(file, *, folder="myApp/uploads", resource_type="image", overwrite=True, eager=None):
    """
    Upload a file-like object to Cloudinary. Returns (secure_url, public_id).
    Optionally pass an 'eager' list for on-the-fly generated variants.
    """
    resp = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type=resource_type,
        overwrite=overwrite,
        eager=eager or None,  # e.g., [{"width": 800, "crop": "scale", "format": "jpg"}]
    )
    return resp.get("secure_url"), resp.get("public_id")
