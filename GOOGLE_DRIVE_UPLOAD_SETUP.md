# Google Drive Upload Integration

This feature allows you to upload images directly from Google Drive to Cloudinary with automatic compression.

## Features

- ✅ Upload single images from Google Drive URLs
- ✅ Bulk upload entire folders from Google Drive
- ✅ Automatic compression for images > 10MB
- ✅ Direct integration with your existing MediaAsset/Album system
- ✅ Supports multiple Google Drive URL formats

## Setup Instructions

### 1. Create a Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

4. Create a Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the service account details
   - Click "Create and Continue"
   - Skip the optional steps and click "Done"

5. Generate a JSON Key:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON" format
   - The file will download automatically

6. Save the JSON file securely (e.g., `google-credentials.json`)

### 2. Share Google Drive Files/Folders

For the service account to access your files:

1. Open the JSON credentials file and find the `client_email` field (looks like: `your-service@your-project.iam.gserviceaccount.com`)
2. In Google Drive, right-click the file or folder you want to upload
3. Click "Share"
4. Add the service account email (from step 1)
5. Give it "Viewer" permission
6. Click "Send"

### 3. Configure Environment Variables

Add to your `.env` file:

```env
# Google Drive Integration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-credentials.json

# Or use an absolute path on Windows:
# GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\google-credentials.json
```

**Note:** You can also place the `google-credentials.json` file in your project root and set:
```env
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
```

### 4. Verify Installation

Make sure the required packages are installed (they should already be in `requirements.txt`):

```bash
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

## API Endpoints

### 1. Upload Single Image

**Endpoint:** `POST /dashboard/gallery/api/google-drive/upload/`

**Request Body (JSON):**
```json
{
  "drive_url": "https://drive.google.com/file/d/1ABC123xyz/view",
  "album_id": 1,  // Optional - MediaAlbum ID
  "tags": "architecture, dubai, villa",  // Optional - comma-separated
  "auto_compress": true  // Optional - default: true
}
```

**Supported URL Formats:**
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- `https://drive.google.com/uc?id=FILE_ID`
- Direct `FILE_ID` (alphanumeric with hyphens)

**Response (Success):**
```json
{
  "success": true,
  "image": {
    "id": 123,
    "title": "Beautiful Villa",
    "secure_url": "https://res.cloudinary.com/...",
    "web_url": "https://res.cloudinary.com/.../f_auto,q_auto/...",
    "thumb_url": "https://res.cloudinary.com/.../c_fill,w_480,h_320/...",
    "public_id": "uploads/beautiful-villa"
  },
  "drive_metadata": {
    "original_name": "Beautiful Villa.jpg",
    "mime_type": "image/jpeg",
    "size": "5242880"
  }
}
```

### 2. Bulk Upload Folder

**Endpoint:** `POST /dashboard/gallery/api/google-drive/bulk-upload/`

**Request Body (JSON):**
```json
{
  "folder_url": "https://drive.google.com/drive/folders/1XYZ789abc",
  "album_id": 1,  // Optional
  "tags": "project, 2024",  // Optional
  "auto_compress": true  // Optional - default: true
}
```

**Response (Success):**
```json
{
  "success": true,
  "uploaded": 15,
  "failed": 0,
  "images": [
    {
      "id": 124,
      "title": "image-1",
      "web_url": "https://res.cloudinary.com/...",
      "drive_name": "image-1.jpg"
    },
    // ... more images
  ],
  "errors": []
}
```

## Usage Examples

### JavaScript/Frontend

```javascript
// Upload single image
async function uploadFromDrive() {
  const response = await fetch('/dashboard/gallery/api/google-drive/upload/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
      drive_url: 'https://drive.google.com/file/d/1ABC123xyz/view',
      tags: 'architecture, villa',
      auto_compress: true
    })
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Uploaded:', data.image);
  } else {
    console.error('Error:', data.error);
  }
}

// Bulk upload folder
async function bulkUploadFromDrive() {
  const response = await fetch('/dashboard/gallery/api/google-drive/bulk-upload/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
      folder_url: 'https://drive.google.com/drive/folders/1XYZ789abc',
      tags: 'project2024',
      auto_compress: true
    })
  });
  
  const data = await response.json();
  console.log(`Uploaded ${data.uploaded} images, ${data.failed} failed`);
}
```

### Python/Django Shell

```python
from myApp.utils.google_drive_utils import upload_from_google_drive_to_cloudinary

# Upload single image
result, web_url, thumb_url, metadata = upload_from_google_drive_to_cloudinary(
    drive_file_id_or_url='https://drive.google.com/file/d/1ABC123xyz/view',
    cloudinary_folder='projects/villa',
    tags=['architecture', 'dubai'],
    auto_compress=True
)

print(f"Uploaded to: {web_url}")
print(f"Original size: {metadata['size']}")
```

## How Compression Works

The system automatically compresses images larger than **~9.3MB** using intelligent compression:

1. **Format Selection:**
   - PNG/TIFF images → WebP format
   - JPEG images → Optimized JPEG
   - WebP images → Stay as WebP

2. **Quality Adjustment:**
   - Starts at 82% quality
   - Iteratively reduces quality until file size fits
   - Minimum quality: 50% (JPEG) or 45% (WebP)

3. **Dimension Scaling:**
   - Maximum width: 5000px
   - Maintains aspect ratio
   - Further scales down if quality reduction isn't enough

4. **EXIF Handling:**
   - Automatically corrects image orientation
   - Preserves color profiles

## Troubleshooting

### "Permission denied" Error

**Problem:** The service account doesn't have access to the file/folder.

**Solution:**
1. Find the service account email in your credentials JSON (`client_email`)
2. Share the Google Drive file/folder with that email
3. Give it at least "Viewer" permission

### "File not found" Error

**Problem:** Invalid file ID or URL format.

**Solution:**
1. Make sure the URL is a valid Google Drive link
2. Check that the file exists and you have access
3. Try copying the file ID directly from the URL

### "Google Drive credentials not found" Error

**Problem:** The `GOOGLE_APPLICATION_CREDENTIALS` environment variable is not set correctly.

**Solution:**
1. Check your `.env` file
2. Ensure the path to the JSON file is correct
3. Use absolute paths if relative paths don't work
4. Restart your Django server after updating `.env`

### Compression Takes Too Long

**Problem:** Large images (>50MB) take a long time to compress.

**Solution:**
1. Pre-resize images before uploading to Google Drive
2. Use the `auto_compress=False` option if you know images are already optimized
3. Consider uploading in smaller batches

## Integration with Existing Gallery

The uploaded images are automatically saved as `MediaAsset` objects and can be:

- Browsed in the Django Admin under "Media assets"
- Selected in the gallery picker for insights/services
- Tagged and organized into albums
- Served with Cloudinary's CDN optimizations

## Security Notes

⚠️ **Important:**
- Never commit your `google-credentials.json` to git
- Add it to `.gitignore`
- Keep service account permissions minimal (Viewer only)
- Rotate credentials periodically
- Use environment-specific service accounts for production

## Next Steps

1. ✅ Set up Google Service Account
2. ✅ Configure environment variables
3. ✅ Share test files with the service account
4. ✅ Test with a single file upload
5. ✅ Try bulk folder upload
6. ✅ Integrate into your dashboard UI

Need help? Check the code in:
- `myApp/utils/google_drive_utils.py` - Core utilities
- `myApp/views.py` - API endpoints (`google_drive_upload`, `google_drive_bulk_upload`)
- `myApp/urls.py` - URL routing

