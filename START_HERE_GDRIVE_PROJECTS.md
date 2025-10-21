# 🚀 START HERE: Google Drive Projects Seed

## What This Does

Automatically seed your **Case Study / Project records** from Google Drive:

```
Google Drive Folder Structure:
├── Greg- The Villa/          → Project 1
│   ├── image1.png [landscape ✓]
│   ├── image2.png [portrait ✗ skip]
├── Jordan Apartment/         → Project 2
└── Jumeira Park/             → Project 3

↓↓↓ (one command) ↓↓↓

Database:
✓ 3 CaseStudy records created
✓ Only landscape images included (width ≥ height)
✓ Hero/thumb/full/gallery URLs assigned
✓ All formset fields populated
```

---

## 5-Minute Quick Start

### Step 1: Set Google Credentials

```powershell
# Windows PowerShell:
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

**Important:** Make sure your service account has **Viewer** access to the folder.

---

### Step 2: Dry Run (Test Mode — No DB Changes)

```bash
cd "E:\New Downloads\Hammer\myProject"

.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --dry-run ^
  --limit=3
```

**What to expect:**
- Lists first 3 project folders
- Shows which images are landscape (kept) vs portrait (skipped)
- Prints what WOULD be created
- **No database writes**

---

### Step 3: Seed One Project (Upload Test)

```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --limit=1
```

**What happens:**
- Processes first project folder
- Uploads landscape images to Cloudinary
- Creates one CaseStudy record
- Verifies entire flow works

---

### Step 4: Verify It Worked

**Check database:**
```bash
.\myenv\Scripts\python.exe manage.py shell
```

```python
from myApp.models import Service, CaseStudy

service = Service.objects.get(slug="interior-design")
print(f"Projects: {service.case_studies.count()}")

for cs in service.case_studies.all():
    print(f"- {cs.title}")
    print(f"  Hero: {cs.hero_image_url}")
    print(f"  Gallery: {len(cs.gallery_urls)} images")
```

**Check UI:**
- Service page: `http://localhost:8000/services/interior-design/`
- Dashboard: `http://localhost:8000/dashboard/services/{id}/edit/`

---

### Step 5: Seed All Projects

If everything looks good:

```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=interior-design ^
  --gallery-max=12
```

**What happens:**
- Processes all project folders
- Uploads all landscape images
- Creates all CaseStudy records
- Limits gallery to 12 images per project

---

## Command Options (Quick Reference)

| Option | Description | Example |
|--------|-------------|---------|
| `--folder-id` | **Required.** GDrive folder ID | `1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5` |
| `--service-slug` | Service to attach to | `interior-design` |
| `--dry-run` | Test mode (no DB writes) | Add flag |
| `--limit` | Process only first N | `--limit=3` |
| `--gallery-max` | Max gallery images | `--gallery-max=12` |
| `--mode` | `skip` or `refresh` | `--mode=refresh` |

---

## Key Features

✅ **Landscape Filtering:** Only images with width ≥ height are included (portraits skipped)

✅ **Idempotent:** Safe to re-run — won't create duplicates

✅ **Dry Run:** Test without writing to database

✅ **Recursive:** Scans all nested subfolders

✅ **Reuses Existing Code:** No upload code duplication

✅ **Comprehensive Logging:** Shows discovered, created, updated, skipped, errors

---

## Folder Structure Rules

```
Root Folder (1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5)
│
├── Project Folder 1/              ← Each immediate child = one project
│   ├── image1.png [1920×1080]     ← ✓ Landscape (width ≥ height)
│   ├── image2.png [1080×1920]     ← ✗ Portrait (skip)
│   └── nested/                    ← Recursively scanned
│       └── image3.png [1600×900]  ← ✓ Landscape
│
├── Project Folder 2/              ← Another project
│   └── ...
```

**Rules:**
- Folder name = Project title
- First landscape image = hero/thumb/full
- Remaining landscape images = gallery
- Portrait images are skipped automatically

---

## Troubleshooting

### "Service not found"

**Solution:** List available services:
```bash
.\myenv\Scripts\python.exe manage.py shell
>>> from myApp.models import Service
>>> for s in Service.objects.all(): print(s.slug)
```

### "Permission denied"

**Solution:** Share folder with service account email (find in your JSON key).

### No images found

**Checklist:**
1. Service account has folder access
2. Folder contains images (not just subfolders)
3. Images are landscape (width ≥ height) — portraits are skipped

---

## Documentation

- **GDRIVE_PROJECTS_README.md** — Complete usage guide ← Start here
- **QUICK_START_GDRIVE_PROJECTS.md** — Quick reference
- **GOOGLE_DRIVE_PROJECTS_SEED.md** — Detailed technical docs
- **GDRIVE_PROJECTS_IMPLEMENTATION.md** — Implementation details

---

## Example Output

```
Seeding Projects for Service: Interior Design
Root GDrive Folder: 1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5
Mode: skip, Gallery Max: 24

🔍 Discovering project folders...
Found 3 project folder(s)
Processing first 3 project(s) only

[1/3] Processing: Greg- The Villa
  → Landscape: greg-the-villa-1.png (1920x1080)
  → Landscape: greg-the-villa-2.png (1600x900)
  ✗ Portrait (skipped): portrait.png (1080x1920)
  ✓ Found 2 landscape image(s)
    ⬆️  Uploading greg-the-villa-1.png...
       ✓ Uploaded: https://res.cloudinary.com/.../greg-the-villa_000.jpg
    ⬆️  Uploading greg-the-villa-2.png...
       ✓ Uploaded: https://res.cloudinary.com/.../greg-the-villa_001.jpg
  ✓ Created: Greg- The Villa (ID: 42)

[2/3] Processing: Jordan Apartment
  ...

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

---

## Next Steps After Seeding

1. **Visit service page** to see projects gallery
2. **Edit in dashboard** to customize:
   - Summary/description text
   - Completion dates
   - Scope/size/timeline labels
   - Tags
   - Featured status
   - Sort order
3. **Refresh mode** to re-sync after folder changes:
   ```bash
   .\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive \
     --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 \
     --service-slug=interior-design \
     --mode=refresh
   ```

---

## 🎯 Summary

You now have a **production-ready** command to seed Case Study records from Google Drive:

1. ✅ **Safe:** Dry-run mode for testing
2. ✅ **Smart:** Only landscape images (width ≥ height)
3. ✅ **Idempotent:** Won't create duplicates
4. ✅ **Fast:** Reuses existing upload infrastructure
5. ✅ **Flexible:** Skip or refresh modes
6. ✅ **Logged:** Comprehensive progress and summary

**Total Setup Time:** < 5 minutes

**Command to Run:**
```bash
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive ^
  --folder-id=1KjNsE9-pKAcBWK4Z-d_UtG70FkHp4sK5 ^
  --service-slug=YOUR_SERVICE_SLUG ^
  --dry-run ^
  --limit=3
```

🎉 **Ready to use!**

