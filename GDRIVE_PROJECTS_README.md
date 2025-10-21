# Google Drive → Case Studies: Automated Project Seeding

## 🎯 What This Does

Automatically creates/updates **Case Study** records by crawling your Google Drive folder structure:

- ✅ **Recursively scans** folders and nested subfolders
- ✅ **Filters strictly to landscape images** (width ≥ height) — portraits are skipped
- ✅ **Uploads to Cloudinary** using your existing infrastructure
- ✅ **Creates CaseStudy records** with all fields populated for your Projects Portfolio
- ✅ **Idempotent** — safe to re-run without creating duplicates
- ✅ **Dry-run mode** — test before writing to database

---

## 📁 Folder Structure Expected

```
Root GDrive Folder: 1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5
│
├── Greg- The Villa/              ← Project 1
│   ├── greg-the-villa-1.png      [1920×1080 → ✓ landscape]
│   ├── greg-the-villa-2.png      [1600×900  → ✓ landscape]
│   ├── portrait.png              [1080×1920 → ✗ skip]
│   └── nested/
│       └── image.png             [1800×1200 → ✓ landscape]
│
├── Jordan Apartment/             ← Project 2
│   ├── Jordan apartment-1.png    [2000×1333 → ✓ landscape]
│   └── subfolder/
│       └── more-images.png
│
└── Jumeira Park/                 ← Project 3
    └── ...
```

**Rules:**
- Each **immediate child folder** = one Project
- Folder name = Project title
- **Only landscape images** (width ≥ height) are included
- All nested subfolders are scanned recursively

---

## 🚀 Quick Start

### Step 1: Verify Prerequisites

**1. Google Drive Access**

Your service account must have **Viewer** access to the folder.

Find your service account email in your credentials JSON:
```json
{
  "client_email": "your-service-account@project.iam.gserviceaccount.com"
}
```

Share the folder with this email (Viewer access).

**2. Set Environment Variable**

```bash
# Linux/Mac:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

**3. Verify Service Exists**

```bash
# Check available services
.\myenv\Scripts\python.exe manage.py shell
>>> from myApp.models import Service
>>> for s in Service.objects.all(): print(s.id, s.slug, s.title)
```

Pick a service slug or ID to use.

---

### Step 2: Dry Run (Test Mode)

**Safely test without writing to database:**

```bash
# Windows:
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --dry-run ^
  --limit=3

# Or use wrapper script:
seed_gdrive_projects.bat ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --dry-run ^
  --limit=3
```

**Expected Output:**
```
🔍 Discovering project folders...
Found 3 project folder(s)
Processing first 3 project(s) only

[1/3] Processing: Greg- The Villa
  → Landscape: greg-the-villa-1.png (1920x1080)
  → Landscape: greg-the-villa-2.png (1600x900)
  ✗ Portrait (skipped): portrait.png (1080x1920)
  ✓ Found 2 landscape image(s)
  [DRY RUN] Would CREATE: Greg- The Villa

[2/3] Processing: Jordan Apartment
  → Landscape: Jordan apartment-1.png (2000x1333)
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

---

### Step 3: Seed One Project (Upload Test)

**Process first project only:**

```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --limit=1
```

**Expected Output:**
```
[1/1] Processing: Greg- The Villa
  → Landscape: greg-the-villa-1.png (1920x1080)
  → Landscape: greg-the-villa-2.png (1600x900)
  ✓ Found 2 landscape image(s)
    ⬆️  Uploading greg-the-villa-1.png...
       ✓ Uploaded: https://res.cloudinary.com/.../projects/greg-the-villa/greg-the-villa_000.jpg
    ⬆️  Uploading greg-the-villa-2.png...
       ✓ Uploaded: https://res.cloudinary.com/.../projects/greg-the-villa/greg-the-villa_001.jpg
  ✓ Created: Greg- The Villa (ID: 42)

✔ Seed complete!
→ Visit /services/interior-design/ to see the projects gallery
```

**Verify in Database:**
```bash
.\myenv\Scripts\python.exe manage.py shell
>>> from myApp.models import CaseStudy
>>> cs = CaseStudy.objects.get(title="Greg- The Villa")
>>> cs.hero_image_url
'https://res.cloudinary.com/.../projects/greg-the-villa/greg-the-villa_000.jpg'
>>> len(cs.gallery_urls)
1
```

---

### Step 4: Seed All Projects

**Process entire folder:**

```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --gallery-max=12
```

**What happens:**
- Processes all project folders
- Uploads all landscape images to Cloudinary
- Creates CaseStudy records
- Limits gallery to 12 images per project (configurable)

---

### Step 5: Re-run (Idempotent Test)

**Verify no duplicates:**

```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design
```

**Expected Output:**
```
[1/N] Processing: Greg- The Villa
  → Already exists (ID: 42). Skipping.

✔ Seed complete!
  Discovered: N
  Created:    0
  Updated:    0
  Skipped:    N
```

---

### Step 6: Refresh Mode (Update Existing)

**Update existing projects with new images:**

```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --mode=refresh
```

**What happens:**
- Projects with matching titles are **updated** (not skipped)
- New projects are created
- Useful for syncing after folder changes

---

## 📋 Command Reference

### Required Options

| Option | Description | Example |
|--------|-------------|---------|
| `--folder-id` | Google Drive root folder ID | `1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5` |
| `--service-slug` | Service to attach projects to | `interior-design` |
| **OR** `--service-id` | Alternative: use service ID | `1` |

### Optional Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dry-run` | False | Test mode (no DB writes) |
| `--limit` | None | Process only first N projects |
| `--gallery-max` | 24 | Max gallery images per project |
| `--mode` | `skip` | `skip` existing or `refresh` (update) |
| `--cloudinary-folder` | `projects` | Cloudinary folder prefix |

---

## 📊 What Gets Created

### CaseStudy Record Fields

| Field | Value | Source |
|-------|-------|--------|
| **service** | Selected service | `--service-slug` or `--service-id` |
| **title** | Folder name (trimmed) | `"Greg- The Villa"` |
| **slug** | Auto-generated | `"greg-the-villa"` |
| **hero_image_url** | First landscape image | Cloudinary URL |
| **thumb_url** | Thumbnail transformation | Cloudinary URL |
| **full_url** | Full-size image | Cloudinary URL |
| **gallery_urls** | Remaining landscape images | JSON array of URLs |
| **summary** | Default text | `"{title} — signature project."` |
| **description** | Default text | `"{title} project seeded from Google Drive."` |
| **completion_date** | NULL | Optional field |
| **scope** | `"Design & Build"` | Default |
| **size_label** | `"Custom"` | Default |
| **timeline_label** | `"12–16 weeks"` | Default |
| **status_label** | `"Completed"` | Default |
| **tags_csv** | `"portfolio,featured"` | Default |
| **cta_url** | Empty | Optional field |
| **is_featured** | False | Default |
| **sort_order** | 0 | Default |

**Note:** You can manually edit these fields in the Django admin or dashboard after seeding.

---

## 🔍 Landscape Filtering

### What Gets Kept

✅ **Landscape images:**
- Width ≥ Height
- Examples: 1920×1080, 1600×900, 1000×1000 (square)

### What Gets Skipped

✗ **Portrait images:**
- Width < Height
- Example: 1080×1920

✗ **Missing metadata:**
- No `imageMediaMetadata.width` or `height`

### Why Landscape Only?

Your Projects Portfolio formset shows hero/thumbnail images in landscape aspect ratios. Portrait images would be cropped or distorted, so they're filtered out automatically.

---

## 🛠️ Troubleshooting

### "Google Drive credentials not found"

**Solution:** Set environment variable:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"
```

### "Permission denied" or "File not found"

**Solution:** Share folder with service account email (Viewer access).

Find email in your JSON key:
```json
{
  "client_email": "your-sa@project.iam.gserviceaccount.com"
}
```

### "Service not found"

**Solution:** List available services:
```bash
.\myenv\Scripts\python.exe manage.py shell
>>> from myApp.models import Service
>>> Service.objects.values_list('id', 'slug', 'title')
```

### No Images Found

**Checklist:**
1. ✓ Service account has folder access
2. ✓ Folder contains images (not just subfolders)
3. ✓ Images are landscape (width ≥ height)
4. ✓ Images have metadata (check in Google Drive)

### Uploads Failing

**Check:**
- Cloudinary credentials in Django settings
- Cloudinary quota (free tier = 25 GB/month)
- Image file sizes (very large images may timeout)

---

## 📚 Additional Documentation

- **QUICK_START_GDRIVE_PROJECTS.md** — Quick reference guide
- **GOOGLE_DRIVE_PROJECTS_SEED.md** — Complete detailed documentation
- **seed_gdrive_projects.bat** — Windows wrapper script
- **seed_gdrive_projects.sh** — Linux/Mac wrapper script

---

## ✅ Acceptance Criteria

- [x] Only landscape images populate hero/thumb/full + gallery
- [x] Each subfolder (one level down from root) seeds exactly one project
- [x] Titles match folder names verbatim (trimmed)
- [x] No code duplication — uses existing `upload_from_google_drive_to_cloudinary()`
- [x] Idempotent — rerunning with no changes does not create duplicates
- [x] Dry-run option prints what would be created/updated
- [x] Logs show: total projects found, skipped (no landscape), created, updated

---

## 🎬 Example Output (Full Run)

```
Seeding Projects for Service: Interior Design
Root GDrive Folder: 1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5
Mode: skip, Gallery Max: 24

🔍 Discovering project folders...
Found 13 project folder(s)

[1/13] Processing: Greg- The Villa
  → Landscape: greg-the-villa-1.png (1920x1080)
  → Landscape: greg-the-villa-2.png (1600x900)
  ✗ Portrait (skipped): portrait.png (1080x1920)
  ✓ Found 2 landscape image(s)
    ⬆️  Uploading greg-the-villa-1.png...
       ✓ Uploaded: https://res.cloudinary.com/.../f_auto,q_auto/projects/greg-the-villa/greg-the-villa_000.jpg
    ⬆️  Uploading greg-the-villa-2.png...
       ✓ Uploaded: https://res.cloudinary.com/.../f_auto,q_auto/projects/greg-the-villa/greg-the-villa_001.jpg
  ✓ Created: Greg- The Villa (ID: 42)

[2/13] Processing: Jordan Apartment
  → Landscape: Jordan apartment-1.png (2000x1333)
  → Landscape: Jordan apartment-2.png (1800x1200)
  ✓ Found 2 landscape image(s)
    ⬆️  Uploading Jordan apartment-1.png...
       ✓ Uploaded: https://res.cloudinary.com/.../projects/jordan-apartment/jordan-apartment_000.jpg
    ⬆️  Uploading Jordan apartment-2.png...
       ✓ Uploaded: https://res.cloudinary.com/.../projects/jordan-apartment/jordan-apartment_001.jpg
  ✓ Created: Jordan Apartment (ID: 43)

... [processing continues for all folders]

============================================================
✔ Seed complete!
  Discovered: 13
  Created:    11
  Updated:    0
  Skipped:    0
  No landscape: 2
  Errors:     0

→ Visit /services/interior-design/ to see the projects gallery
→ Total Case Studies for this service: 11
```

---

## 🎯 Summary

You now have a **production-ready** command to automatically seed Case Study records from Google Drive:

1. ✅ **Safe testing** with `--dry-run` and `--limit`
2. ✅ **Landscape-only filtering** (width ≥ height)
3. ✅ **Idempotent operations** (no duplicates)
4. ✅ **Comprehensive logging** (discover, create, update, skip, error counts)
5. ✅ **Reuses existing infrastructure** (no upload code duplication)

**Next Steps:**
1. Run dry-run test (`--dry-run --limit=3`)
2. Seed one project (`--limit=1`)
3. Verify in database and UI
4. Seed all projects
5. Manually edit default fields (summary, description, etc.) in dashboard

