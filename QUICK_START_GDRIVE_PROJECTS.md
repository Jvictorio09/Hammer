# Quick Start: Seed Projects from Google Drive

## One-Command Setup

```bash
# Set your Google credentials (if not already set)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

## Usage Examples

**Windows Users:** Use `.\myenv\Scripts\python.exe` instead of `python`, or use the wrapper script `seed_gdrive_projects.bat`

### 1. Dry Run (Safe Test - No DB Changes)

```bash
# Linux/Mac:
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --dry-run \
  --limit=3

# Windows:
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design --dry-run --limit=3

# Or use the wrapper script:
seed_gdrive_projects.bat --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design --dry-run --limit=3
```

**What it does:**
- Lists first 3 project folders
- Shows which images are landscape (kept) vs portrait (skipped)
- Prints what WOULD be created (no database writes)

### 2. Seed One Project (Test Upload)

```bash
# Linux/Mac:
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --limit=1

# Windows:
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design --limit=1
```

**What it does:**
- Processes first project folder
- Uploads landscape images to Cloudinary
- Creates one CaseStudy record
- Verifies everything works end-to-end

### 3. Seed All Projects

```bash
# Linux/Mac:
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --gallery-max=12

# Windows:
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design --gallery-max=12
```

**What it does:**
- Processes all project folders
- Uploads all landscape images
- Creates all CaseStudy records
- Limits gallery to 12 images per project

### 4. Refresh Existing Projects

```bash
# Linux/Mac:
python manage.py seed_projects_from_gdrive \
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
  --service-slug=interior-design \
  --mode=refresh

# Windows:
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 --service-slug=interior-design --mode=refresh
```

**What it does:**
- Updates existing projects (same title = update)
- Creates new projects (new title = create)
- Useful for re-syncing after folder changes

---

## Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--folder-id` | **Required.** GDrive root folder ID | `1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5` |
| `--service-slug` | Service to attach projects to | `interior-design` |
| `--service-id` | Alternative: use service ID | `1` |
| `--dry-run` | Test mode (no DB writes) | Add flag |
| `--limit` | Process only first N projects | `--limit=3` |
| `--gallery-max` | Max gallery images per project | `--gallery-max=12` |
| `--mode` | `skip` (default) or `refresh` | `--mode=refresh` |

---

## What Gets Created

Each immediate child folder in the GDrive folder becomes **one Project**:

```
Root Folder (1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5)
├── Greg- The Villa/          → Project 1
│   ├── image1.png [landscape ✓]
│   ├── image2.png [portrait ✗ skipped]
│   └── subfolder/
│       └── image3.png [landscape ✓]
├── Jordan Apartment/         → Project 2
└── Jumeira Park/             → Project 3
```

**Key Rules:**
- ✅ Only **landscape images** (width ≥ height) are included
- ✅ Recursively scans all nested subfolders
- ✅ First landscape image → hero/thumb/full
- ✅ Remaining landscape images → gallery

---

## Verification Steps

### 1. Check Projects Were Created

```bash
python manage.py shell
```

```python
from myApp.models import Service, CaseStudy

# Find your service
service = Service.objects.get(slug="interior-design")

# Count projects
print(f"Projects: {service.case_studies.count()}")

# List projects
for cs in service.case_studies.all():
    print(f"- {cs.title} (ID: {cs.id})")
    print(f"  Hero: {cs.hero_image_url}")
    print(f"  Gallery: {len(cs.gallery_urls)} images")
```

### 2. View in Browser

Visit: `http://localhost:8000/services/interior-design/`

Or dashboard: `http://localhost:8000/dashboard/services/{service_id}/edit/`

---

## Troubleshooting

### "Service not found"

**Solution:** Create a service first or use an existing service slug.

List available services:
```bash
python manage.py shell
>>> from myApp.models import Service
>>> for s in Service.objects.all(): print(s.slug)
```

### "Google Drive credentials not found"

**Solution:** Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
```

### "Permission denied"

**Solution:** Share the folder with your service account email.

Find service account email in your JSON key:
```json
{
  "client_email": "your-sa@project.iam.gserviceaccount.com",
  ...
}
```

Go to Google Drive → Right-click folder → Share → Add service account email → Viewer access

### No Images Found

**Checklist:**
1. Folder contains images (not just subfolders)
2. Images are landscape (width ≥ height) — portraits are skipped
3. Images have metadata (check in Google Drive)

---

## Full Documentation

See `GOOGLE_DRIVE_PROJECTS_SEED.md` for complete details.

