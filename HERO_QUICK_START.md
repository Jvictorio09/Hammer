# Hero Management - Quick Start Guide

## 🚀 Setup in 3 Steps

### Step 1: Run Migration

Open your terminal and run:

```bash
# Windows PowerShell
cd "E:\New Downloads\Hammer\myProject"
python manage.py migrate
```

This creates the `PageHero` database table.

---

### Step 2: Seed Default Heroes (Optional)

```bash
python seed_heroes.py
```

This creates hero content for all 6 pages (only Home is active by default).

---

### Step 3: Access Dashboard

1. Open browser: `http://localhost:8000/dashboard/`
2. Login as superuser
3. Click **"🎨 Page Heroes"**
4. Edit the Home hero or create new ones!

---

## 📝 Example: Edit Home Hero

1. Go to `/dashboard/heroes/`
2. Click **"Edit"** on the Home hero card
3. Change the **Headline** to: `"Transform your outdoor space with expert design"`
4. Update **Hero Image URL**: Paste a Cloudinary URL
5. Click **"Save Changes"**
6. Visit your homepage to see the changes! 🎉

---

## 🎨 Button & Pills Format

### Buttons (copy & paste this):
```json
[
  {
    "text": "View Our Work",
    "url": "/projects/",
    "style": "outline"
  },
  {
    "text": "Get Started",
    "url": "/contact/",
    "style": "filled",
    "icon": "fa-solid fa-arrow-right"
  }
]
```

### Pills (copy & paste this):
```json
[
  "20+ years experience",
  "1000+ projects delivered",
  "Dubai-based team"
]
```

---

## ✅ What's Working

- ✅ Hero management dashboard
- ✅ Create/Edit/Delete heroes for any page
- ✅ Home page integration complete
- ✅ Safe fallback to default content
- ✅ Superuser-only access

---

## 🔧 Integrate Other Pages

To add heroes to other pages, edit their views in `myApp/views.py`:

**Before:**
```python
def about(request):
    return render(request, "about.html", {
        # ... context
    })
```

**After:**
```python
def about(request):
    hero = PageHero.get_hero_for_page('about')
    return render(request, "about.html", {
        "hero": hero,  # ← Add this
        # ... context
    })
```

Make sure to import at the top:
```python
from .models import PageHero
```

---

## 🎯 Quick Tips

1. **Use Cloudinary URLs** for images (already optimized)
2. **Test on mobile** after making changes
3. **Keep headlines short** (under 80 characters)
4. **Use 1-2 buttons max** for clarity
5. **Validate JSON** before saving (the form will highlight errors)

---

## 🆘 Troubleshooting

**Hero not showing?**
- Check if it's marked as "Active" ✅
- Clear browser cache
- Check browser console for errors

**JSON errors?**
- Use a JSON validator: https://jsonlint.com/
- Check for missing commas or quotes
- See examples in the form (expand "Show example")

**Permission denied?**
- Make sure you're logged in as superuser
- Regular users can't access hero management

---

## 🎉 You're Done!

Your hero management system is ready to use. No more code changes needed to update hero sections!

Need help? Check `HERO_MANAGEMENT_README.md` for full documentation.

