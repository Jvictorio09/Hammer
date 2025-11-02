# 🏷️ Page Metadata Management System

Complete SEO metadata management for your website.

## ✅ What's Included

- **PageMetadata Model**: Database model with 140-character title fields
- **Dashboard Interface**: Full CRUD at `/dashboard/metadata/`
- **26 Pre-filled URLs**: Seed script with starter metadata
- **Auto-injection**: Meta tags automatically applied to all pages
- **Navigation**: Easy access from dashboard sidebar

## 🚀 Setup Instructions

### Step 1: Run Migrations

Create the PageMetadata table:

```bash
cd myProject
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Seed Initial Metadata

Populate 26 existing URLs with starter metadata:

```bash
python seed_metadata.py
```

You'll see output like:
```
============================================================
SEEDING PAGE METADATA
============================================================
✅ Created: 26 entries
⏭️  Skipped: 0 entries (already exist)
📊 Total: 26 entries
============================================================
Metadata seeding complete!
```

### Step 3: Access Dashboard

Visit: `/dashboard/metadata/`

You can now:
- ✏️ Edit any of the 26 pre-filled URLs
- ➕ Add new metadata entries
- 🗑️ Delete entries you don't need
- 👀 See metadata automatically appear on all pages

## 📋 Pre-filled URLs

All major pages are pre-filled with SEO metadata:
- Home, About, Contact
- Services, Projects, Insights
- Landscape, Interior, Facility
- Legacy URLs (with and without trailing slashes)

## 🎨 Features

- ✅ 140-character titles (no migration issues!)
- ✅ 200-character descriptions
- ✅ Keywords support
- ✅ Open Graph tags for social sharing
- ✅ Active/Inactive toggle
- ✅ Character counters with warnings
- ✅ Search & filter in dashboard

## 📝 Usage

1. Go to Dashboard → Metadata
2. Click "Add Metadata" or edit existing
3. Fill in:
   - Page Name: Human-readable identifier
   - URL Path: e.g., `/about/` (must start with /)
   - Meta Title: SEO title (50-70 chars recommended)
   - Meta Description: Description (150-160 chars recommended)
   - OG Title/Description/Image: For social media
4. Click "Create Metadata"
5. Metadata automatically appears on the page!

## 🔍 How It Works

The `page_metadata` context processor:
1. Checks the current URL path
2. Looks up PageMetadata for that path
3. Injects meta tags into `<base.html>`
4. Falls back to defaults if no metadata found

All done automatically - no code changes needed per page!

## 🎯 Ready for Semrush

Your metadata is now managed centrally and will improve:
- Search engine rankings
- Social media previews
- Click-through rates
- Overall SEO score

---

**Need to re-run seeding?** Just run `python seed_metadata.py` again - it's idempotent!

