# Quick Start: Google Drive Upload

## ✅ What's New

You can now upload images directly from Google Drive to Cloudinary with automatic compression!

### Features Added:
- 🔵 **New "Drive" tab** in the service form upload modal
- 🗜️ **Automatic compression** for images larger than 10MB
- 📦 **API endpoints** for programmatic uploads
- 🔒 **Secure** - uses Google Service Account authentication

---

## 🚀 Quick Setup (3 steps)

### 1. Get Google Credentials

1. Go to https://console.cloud.google.com/
2. Create project → Enable Google Drive API
3. Create Service Account → Download JSON key
4. Save as `google-credentials.json` in your project root

### 2. Add to .env

```env
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
```

### 3. Share Files with Service Account

1. Open your `google-credentials.json`
2. Find the `client_email` (looks like: `xxx@xxx.iam.gserviceaccount.com`)
3. In Google Drive, share your files/folders with that email (Viewer permission)

---

## 📝 How to Use

### In the Dashboard

1. Go to **Dashboard → Services → Edit Service**
2. Click **"Browse Gallery"** for any image field
3. Click the **"Drive"** tab  
4. Paste your Google Drive shareable link
5. Click **"Upload from Drive"**
6. Done! The image is automatically compressed and uploaded to Cloudinary

### Supported URL Formats

All these work:
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- Direct FILE_ID

---

## 🧪 Test Your Setup

Run the test script to verify everything works:

```bash
cd myProject
python test_google_drive_upload.py
```

This will check:
✓ Credentials configured  
✓ Google Drive connection  
✓ File download  
✓ Cloudinary upload (optional)

---

## 🔧 How It Works

1. **Download**: Image is downloaded from Google Drive
2. **Compress**: If > 10MB, automatically compressed (WebP/JPEG)
3. **Upload**: Uploaded to Cloudinary
4. **Save**: URL saved to your MediaAsset library

### Compression Details

- **Trigger**: Files > ~9.3MB
- **Format**: PNG/TIFF → WebP, JPEG → optimized JPEG
- **Quality**: Starts at 82%, reduces until under limit
- **Max Width**: 5000px (maintains aspect ratio)

---

## 💡 Tips

### Make Files Shareable
```
Right-click file in Drive → Share → Add service account email → Viewer
```

### Bulk Upload a Folder
Use the API endpoint for folders:
```javascript
fetch('/dashboard/gallery/api/google-drive/bulk-upload/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    folder_url: 'https://drive.google.com/drive/folders/YOUR_FOLDER_ID',
    auto_compress: true
  })
})
```

---

## 🐛 Troubleshooting

### "Permission denied"
→ File not shared with service account. Share it with the email from your JSON file.

### "Google Drive credentials not found"
→ Check `.env` file has `GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json`
→ Restart your Django server after updating `.env`

### "File not found"
→ Check the URL is correct and the file exists
→ Make sure it's shared with the service account

---

## 📚 Full Documentation

See `GOOGLE_DRIVE_UPLOAD_SETUP.md` for detailed documentation including:
- Step-by-step Google Cloud setup
- API endpoint reference
- JavaScript examples
- Python usage examples
- Security best practices

---

## ✨ That's It!

Your existing upload methods still work exactly the same:
- 📷 **Gallery tab** - browse uploaded images
- ⬆️ **Upload tab** - upload from computer  
- 🔵 **Drive tab** - NEW! upload from Google Drive

All three options are available side-by-side in the same modal. Pick whichever is most convenient!

