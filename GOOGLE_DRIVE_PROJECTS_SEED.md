# Google Drive Projects Seed - Complete Guide

Automatically seed Case Study / Project records by crawling a Google Drive folder containing project subfolders with images.

## Overview

This management command:
- ✅ Recursively crawls a Google Drive folder and all nested subfolders
- ✅ Treats each **immediate child folder** as one Project (title = folder name)
- ✅ **Filters strictly to landscape images** (width ≥ height) — portraits are skipped
- ✅ Uploads images to Cloudinary using your existing `upload_gdrive_file_to_cloudinary` function
- ✅ Populates all CaseStudy model fields that power your Projects Portfolio formset
- ✅ Provides idempotent operations with `skip` or `refresh` modes
- ✅ Includes dry-run and limit options for safe testing

---

## Prerequisites

### 1. Google Drive Setup

Your service account must have **Viewer** access to the target folder.

**Root Folder ID:** `1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5`

### 2. Environment

Ensure `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to your service account JSON:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

Or on Windows:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

### 3. Django Setup

Make sure you have:
- Django project configured
- Cloudinary credentials in settings
- Service record to attach projects to

---

## Usage

### Basic Command

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design
```

### With Service ID

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-id=1
```

### Dry Run (Safe Testing)

Test without writing to database:

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --dry-run \
  --limit=3
```

### Refresh Mode

Update existing projects instead of skipping them:

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --mode=refresh \
  --gallery-max=12
```

---

## Command Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--folder-id` | **Yes** | — | Google Drive root folder ID to crawl |
| `--service-id` | One of these | — | Service ID to attach projects to |
| `--service-slug` | One of these | — | Service slug to attach projects to |
| `--limit` | No | None | Process only first N projects (for testing) |
| `--gallery-max` | No | 24 | Maximum gallery images per project |
| `--mode` | No | `skip` | `skip` existing projects or `refresh` (update) them |
| `--dry-run` | No | False | Don't write to DB, only log proposed actions |
| `--cloudinary-folder` | No | `projects` | Cloudinary folder prefix for uploads |

---

## How It Works

### 1. Folder Structure

```
Root GDrive Folder (1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5)
├── Greg- The Villa/              ← Project 1 (title = "Greg- The Villa")
│   ├── greg- the villa-1.png     [landscape: ✓]
│   ├── greg- the villa-2.png     [landscape: ✓]
│   └── portrait.png              [portrait: ✗ skipped]
├── Jordan Apartment/             ← Project 2 (title = "Jordan Apartment")
│   ├── subfolder/                (recursively included)
│   │   └── image.png
│   └── Jordan apartment-1.png
└── Jumeira Park/                 ← Project 3
    └── ...
```

### 2. Image Filtering (Landscape Only)

- ✅ **Keep:** `width >= height` (landscape or square)
- ✗ **Skip:** `width < height` (portrait)
- ✗ **Skip:** Missing `imageMediaMetadata.width` or `height`

**Example:**
- 1920×1080 → ✓ Keep
- 1080×1920 → ✗ Skip (portrait)
- 1000×1000 → ✓ Keep (square)

### 3. Image Assignment

For each project:

- **First landscape image** → `hero_image_url`, `thumb_url`, `full_url`
- **Remaining images** (up to `--gallery-max`) → `gallery_urls` (JSON array)

### 4. Field Mapping

| Template Field | Model Field | Value Source |
|----------------|-------------|--------------|
| Project Title | `title` | Folder name (trimmed) |
| Hero (Detail Page) | `hero_image_url` | First landscape image |
| Thumbnail (Gallery) | `thumb_url` | Same as hero (Cloudinary transformation) |
| Full Size (Gallery) | `full_url` | Same as hero (original) |
| Gallery Images | `gallery_urls` | Array of remaining landscape images |
| Summary | `summary` | `"{title} — signature project."` |
| Description | `description` | `"{title} project seeded from Google Drive."` |
| Completion Date | `completion_date` | `NULL` (optional) |
| Scope | `scope` | `"Design & Build"` |
| Size | `size_label` | `"Custom"` |
| Timeline | `timeline_label` | `"12–16 weeks"` |
| Status | `status_label` | `"Completed"` |
| Tags | `tags_csv` | `"portfolio,featured"` |
| CTA URL | `cta_url` | Empty |
| Featured | `is_featured` | `False` |
| Order | `sort_order` | `0` |
| Slug | `slug` | Auto-generated from title |

### 5. Idempotency

**Skip Mode (default):**
- If a project with the same `title` exists → skip it
- No duplicates created

**Refresh Mode:**
- If a project exists → update all fields with new data
- Useful for re-syncing after folder changes

---

## Example Workflow

### Step 1: Dry Run (Test)

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --dry-run \
  --limit=3
```

**Output:**
```
[DRY RUN] Seeding Projects for Service: Interior Design
Root GDrive Folder: 1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5
Mode: skip, Gallery Max: 24

🔍 Discovering project folders...
Found 3 project folder(s)
Processing first 3 project(s) only

[1/3] Processing: Greg- The Villa
  → Landscape: greg- the villa-1.png (1920x1080)
  → Landscape: greg- the villa-2.png (1600x900)
  ✗ Portrait (skipped): portrait.png (1080x1920)
  ✓ Found 2 landscape image(s)
  [DRY RUN] Would CREATE: Greg- The Villa

[2/3] Processing: Jordan Apartment
  → Landscape: Jordan apartment-1.png (1800x1200)
  ✓ Found 1 landscape image(s)
  [DRY RUN] Would CREATE: Jordan Apartment

[3/3] Processing: Jumeira Park
  ⚠️  No landscape images found. Skipping.

============================================================
✔ Seed complete!
  Discovered: 3
  Created:    2
  Updated:    0
  Skipped:    0
  No landscape: 1
  Errors:     0
```

### Step 2: Run for Real (Create Projects)

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --limit=3
```

**Output:**
```
Seeding Projects for Service: Interior Design
...
[1/3] Processing: Greg- The Villa
    ⬆️  Uploading greg- the villa-1.png...
       ✓ Uploaded: https://res.cloudinary.com/.../f_auto,q_auto/projects/greg-the-villa/greg-the-villa_000.jpg
    ⬆️  Uploading greg- the villa-2.png...
       ✓ Uploaded: https://res.cloudinary.com/.../f_auto,q_auto/projects/greg-the-villa/greg-the-villa_001.jpg
  ✓ Created: Greg- The Villa (ID: 42)

============================================================
✔ Seed complete!
  Discovered: 3
  Created:    2
  Updated:    0
  Skipped:    0
  No landscape: 1
  Errors:     0

→ Visit /services/interior-design/ to see the projects gallery
→ Total Case Studies for this service: 2
```

### Step 3: Re-run (Idempotent)

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design
```

**Output:**
```
...
[1/3] Processing: Greg- The Villa
  → Already exists (ID: 42). Skipping.

[2/3] Processing: Jordan Apartment
  → Already exists (ID: 43). Skipping.

============================================================
✔ Seed complete!
  Discovered: 3
  Created:    0
  Updated:    0
  Skipped:    2
  No landscape: 1
  Errors:     0
```

---

## Edge Cases & Policies

### No Landscape Images

If a project folder contains **only portrait images** or no images:
- ⚠️ Project is skipped (not created)
- Logged as "No landscape images found"

### Gigantic Images

Your existing Cloudinary transformations handle resizing:
- Uploaded with `f_auto,q_auto` for web delivery
- Thumbnails created with `c_fill,g_face,w_480,h_320`

### Folder Renames

If you rename a folder in Google Drive:
- **Skip mode:** Treated as a new project (new title = new project)
- **Refresh mode:** Existing project not updated (title doesn't match)

**Recommendation:** Use folder name as canonical identifier. Don't rename folders after seeding.

### Missing Metadata

Some images may not have `imageMediaMetadata.width` or `height`:
- ✗ These are skipped (we only want confirmed landscape images)

---

## Troubleshooting

### Error: "Google Drive credentials not found"

**Solution:** Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Error: "Permission denied"

**Solution:** Share the root folder with your service account email (Viewer access).

Find service account email in your JSON key:
```json
{
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  ...
}
```

### Error: "Service not found"

**Solution:** Verify service exists:
```bash
python manage.py shell
>>> from myApp.models import Service
>>> Service.objects.all()
>>> Service.objects.get(slug="interior-design")
```

### No Images Found

**Checklist:**
- ✓ Service account has access to folder
- ✓ Folder contains images (not just subfolders)
- ✓ Images are landscape (width ≥ height)
- ✓ Images have metadata (check in Drive)

---

## Advanced Usage

### Custom Cloudinary Folder

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --cloudinary-folder=portfolio/interiors
```

### Gallery Size Limit

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --gallery-max=8
```

### Process All Projects (No Limit)

```bash
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design
```

---

## Smoke-Test Checklist

- [ ] **Auth:** Service account has Viewer access to root folder
- [ ] **Dry Run:** Test with `--dry-run --limit=3` → verify project titles and image counts
- [ ] **One Project:** Run with `--limit=1` → verify 1 project created with hero + gallery
- [ ] **Idempotent:** Re-run same command → expect "exists/skip" with zero duplicates
- [ ] **UI Check:** Load service page → confirm hero/thumbnail/full appear in gallery
- [ ] **Landscape Filter:** Verify only landscape images (width ≥ height) are included

---

## Technical Details

### Existing Functions Used

- `get_drive_service()` — Initialize Google Drive API client
- `upload_from_google_drive_to_cloudinary(file_id, ...)` — Upload image to Cloudinary

**No code duplication** — reuses your existing upload infrastructure.

### Database Fields

Matches your `CaseStudy` model exactly:

```python
class CaseStudy(models.Model):
    service = models.ForeignKey('Service', ...)
    title = models.CharField(max_length=220)
    slug = models.SlugField(unique=True, blank=True)
    hero_image_url = models.URLField()
    thumb_url = models.URLField(blank=True)
    full_url = models.URLField(blank=True)
    gallery_urls = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    completion_date = models.DateField(null=True, blank=True)
    scope = models.CharField(max_length=100, blank=True)
    size_label = models.CharField(max_length=100, blank=True)
    timeline_label = models.CharField(max_length=100, blank=True)
    status_label = models.CharField(max_length=100, blank=True)
    tags_csv = models.CharField(max_length=300, blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    cta_url = models.URLField(blank=True)
```

### Rate Limits

- Google Drive API: 1,000 queries per 100 seconds per user
- Cloudinary: Free tier → 25 GB/month bandwidth

**Recommendation:** Use `--limit` for large folders to batch uploads.

---

## Support

For issues or questions:
1. Check this documentation
2. Run with `--dry-run` to debug
3. Verify Google Drive permissions
4. Check Django logs for detailed errors

---

## Summary

✅ **Use this command to:**
- Automatically seed projects from Google Drive
- Filter strictly to landscape images (width ≥ height)
- Upload to Cloudinary with your existing infrastructure
- Populate all CaseStudy fields for your Projects Portfolio formset
- Run safely with dry-run and idempotent modes

✅ **Key Features:**
- Recursive folder crawling
- Landscape-only filtering
- Idempotent operations
- Dry-run testing
- Comprehensive logging

✅ **Perfect for:**
- Initial project seeding
- Bulk imports from Google Drive
- Keeping portfolio in sync with Drive folders

