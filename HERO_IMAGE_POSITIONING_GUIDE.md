# Hero Image Positioning Guide

## 📋 Overview

This document explains how hero image positioning works in the Hammer Group website and provides two implementation approaches.

---

## 🎯 Current Implementation: CSS Position Adjustment (NO Cropping)

### How It Works

1. **Upload full-resolution images** - No cropping needed
2. **Adjust focal point** using the Position Adjuster tool
3. **CSS handles display** - Uses `background-position` or `object-position`
4. **Frontend matches preview** - What you see is what visitors get

### Technical Details

#### Database Field
```python
# models.py - Service Model
hero_image_position = models.CharField(
    max_length=50, 
    default='50% 40%',
    help_text="CSS background-position for hero image (e.g., '50% 40%')"
)
```

#### Frontend Display
```html
<!-- service_detail.html -->
<img
  src="{{ service.hero_media_url }}"
  alt="{{ service.title }} hero"
  class="absolute inset-0 w-full h-full object-cover"
  style="object-position: {{ service.hero_image_position|default:'50% 40%' }};"
>
```

#### Dashboard Tool
- **21:9 aspect ratio preview** - Matches actual service page heroes
- **Live preview** - See exactly what visitors will see
- **9 quick presets** - Top-Left, Center, Bottom-Right, etc.
- **Fine-tune sliders** - Horizontal (0-100%) and Vertical (0-100%)

### Position Values Explained

```
Format: X% Y%
- X = Horizontal position (0% = left, 50% = center, 100% = right)
- Y = Vertical position (0% = top, 50% = middle, 100% = bottom)

Examples:
- "50% 40%" - Center horizontally, slightly above center (DEFAULT - best for interiors)
- "50% 30%" - Center horizontally, upper third (good for rooms with interesting ceilings)
- "0% 50%" - Left side, middle vertically
- "100% 50%" - Right side, middle vertically
```

### Benefits

✅ **No data loss** - Keep full resolution images  
✅ **Flexible** - Reposition anytime without re-uploading  
✅ **Efficient** - One image works across different views  
✅ **No storage waste** - No duplicate cropped versions  
✅ **Easy updates** - Change position in 30 seconds  

### Best Practices

**For Interior Photos:**
- Use **30-40% vertical** to avoid ceiling views
- Most interior shots look best at `50% 35%` or `50% 40%`

**For Landscape Photos:**
- Use **40-50% vertical** to center horizon
- Try `50% 45%` as a starting point

**For Product/Detail Shots:**
- Use **50% 50%** (perfect center)
- Adjust based on subject location

---

## 💾 Alternative: Actual Image Cropping (If You Prefer)

If you want to **save cropped versions** instead, here's how it would work:

### Pros
✅ Fixed composition - no CSS positioning needed  
✅ Can apply filters/adjustments during crop  
✅ Smaller file sizes (only cropped portion uploaded)  

### Cons
❌ Lost data - original full image not preserved  
❌ Can't reposition without re-uploading original  
❌ Storage waste - need both original + cropped versions  
❌ Slower workflow - cropping takes time  

### Implementation (If Requested)

**Would require:**
1. Keep Cropper.js (the one we removed)
2. Add server-side image processing
3. Upload cropped version to Cloudinary
4. Store cropped URL in database
5. Display cropped image on frontend

**Workflow would be:**
1. Upload full image
2. Open crop modal
3. Select crop area (21:9 aspect ratio)
4. Click "Save Crop"
5. System crops image server-side
6. Uploads to Cloudinary as `hero-cropped-{id}.webp`
7. Stores cropped URL in database
8. Frontend displays cropped version

---

## 🔧 How to Use the Position Adjuster

### Step-by-Step Instructions

1. **Go to Dashboard** → Services → Click "Edit" on any service

2. **Scroll to Hero Section** → Find "Hero Image Position (Focal Point)"

3. **Click "Adjust" button** → Opens the Position Adjuster modal

4. **See Live Preview** → Shows exactly how image will appear on site
   - 21:9 aspect ratio (matches service pages)
   - Real hero text overlay
   - Current position displayed in bottom-right

5. **Choose Adjustment Method:**
   - **Quick Presets** - Click any of 9 position buttons
   - **Fine-Tune Sliders** - Drag horizontal/vertical sliders for precision

6. **Watch Preview Update** - Changes happen instantly

7. **Click "Apply Position"** - Saves the new position

8. **Save Service** - Don't forget to save the form!

### Troubleshooting

**Q: Preview doesn't match my live site**  
A: Check console logs (F12) for debug output. Should show current position being loaded.

**Q: Changes don't save**  
A: Make sure you click both "Apply Position" AND "Save" on the main form.

**Q: Position resets to 50% 40%**  
A: Database might not have value set. Check migration was run: `python manage.py migrate`

**Q: Can't see full image in preview**  
A: That's intentional! Preview shows what visitors see (cover mode). Use sliders to reposition.

---

## 🔍 Technical Implementation Details

### Files Modified

| File | Changes |
|------|---------|
| `models.py` | Added `hero_image_position` field to Service |
| `forms.py` | Added field to ServiceForm |
| `service_form.html` | Added Position Adjuster UI + modal |
| `service_detail.html` | Added `object-position` style |
| `migrations/0021_*.py` | Migration for new field |
| `migrations/0022_*.py` | Data migration (set defaults) |

### Database Schema

```sql
ALTER TABLE myApp_service 
ADD COLUMN hero_image_position VARCHAR(50) 
DEFAULT '50% 40%';
```

### CSS Implementation

**Option 1: Background Image** (for `::before` pseudo-elements)
```css
.hero::before {
  background-image: url('hero.jpg');
  background-size: cover;
  background-position: 50% 40%; /* From database */
}
```

**Option 2: IMG Tag** (preferred for better performance)
```css
img.hero {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 40%; /* From database */
}
```

---

## 📊 Comparison Table

| Feature | Position Adjustment | Actual Cropping |
|---------|-------------------|----------------|
| Data Loss | None | Yes (cropped data lost) |
| Storage Used | 1 image | 2 images (original + cropped) |
| Flexibility | High (reposition anytime) | Low (must re-crop) |
| Speed | Instant (CSS change) | Slow (upload cropped version) |
| File Size | Larger (full image) | Smaller (only crop) |
| Quality | Best (full resolution) | Good (cropped resolution) |
| Implementation | **Current ✅** | Would need to implement |

---

## 🚀 Recommended Workflow

1. **Upload high-resolution image** (1920×1080 minimum, 2560×1440 ideal)
2. **Use Position Adjuster** to find perfect focal point
3. **Test on live site** to verify
4. **Adjust if needed** - takes 30 seconds

### Pro Tips

- Take photos with **extra space** around subject (easier to reposition)
- **Avoid tight crops** - let the position adjuster handle framing
- **Test multiple positions** - use Reset button freely
- **Save presets** mentally for consistency (e.g., all interior shots at 50% 35%)

---

## 🎓 Understanding CSS `background-position`

### Visual Guide

```
┌─────────────────────────┐
│ 0% 0%      50% 0%  100% 0%│ Top
│   ↖         ↑        ↗   │
│                           │
│ 0% 50%     50% 50% 100% 50%│ Middle
│   ←         ●        →   │
│                           │
│ 0% 100%   50% 100% 100% 100%│ Bottom
│   ↙         ↓        ↘   │
└─────────────────────────┘
```

### How It Works with `cover`

When using `background-size: cover` or `object-fit: cover`:

1. Image scales to fill container completely
2. Maintains aspect ratio
3. Crops overflow based on `background-position`
4. Position determines which part stays visible

**Example:**
- Container: 1920×500px (21:9 ratio)
- Image: 2000×1500px
- `background-position: 50% 40%`
  - Horizontally: Center the image (50%)
  - Vertically: Show from 40% down (slightly above center)
  - Result: Bottom 60% of image is cut off, top 40% is visible

---

## 📝 Migration Log

### What We Changed

**Before:** Images were cropped manually, losing data  
**After:** Full images stored, position adjusted via CSS

**Migration Steps:**
1. Added `hero_image_position` field to Service model
2. Created migration (0021)
3. Set default `50% 40%` for existing services (0022)
4. Updated templates to use position
5. Removed Cropper.js
6. Added Position Adjuster modal

**Database Impact:**
- 4 existing services updated with default position
- No image re-uploads needed
- All existing images work perfectly

---

## 🆘 Support & Questions

**Need actual cropping instead?**  
Let me know and I can implement the alternative approach.

**Position not working?**  
1. Check browser console (F12) for errors
2. Verify migration ran: `python manage.py showmigrations myApp`
3. Check database: Service should have `hero_image_position` column

**Want different default?**  
Change in `models.py`: `default='50% 40%'` → your preferred value

---

## 📅 Version History

- **v1.0** (Oct 27, 2025) - Initial implementation with Position Adjuster
- Replaced Cropper.js with focal point control
- Added live preview with 21:9 aspect ratio
- Migrated 4 existing services to use default position

---

**Created by:** AI Assistant  
**Last Updated:** October 27, 2025  
**Current Implementation:** CSS Position Adjustment (Recommended ✅)

