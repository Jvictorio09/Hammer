# Page Hero Management System

## Overview

The Page Hero Management system allows superusers to dynamically customize hero sections (the large banner at the top of pages) for each page on your website through the dashboard. No code changes needed!

## Features

✅ **Dynamic Content**: Update hero images, headlines, and CTAs from the dashboard  
✅ **Per-Page Customization**: Different hero content for Home, About, Services, Projects, Insights, and Contact  
✅ **Flexible Buttons**: Configure multiple CTA buttons with custom text, links, and styles  
✅ **Feature Pills**: Add small feature highlights below CTAs  
✅ **Safe Fallback**: Pages without custom heroes use default content (no breaking changes)  
✅ **Superuser Only**: Only admins/superusers can manage heroes

---

## Getting Started

### 1. Apply Database Migration

First, apply the migration to create the `PageHero` table:

```bash
# On Windows (with virtual environment)
cd myProject
.\myenv\Scripts\activate
python manage.py migrate

# On Linux/Mac
cd myProject
source myenv/bin/activate
python manage.py migrate
```

### 2. Seed Default Heroes (Optional)

To create default hero content for all pages:

```bash
python seed_heroes.py
```

This will create heroes for all 6 pages (only the home hero is active by default).

---

## Using the Dashboard

### Access Hero Management

1. Log in as a superuser
2. Go to `/dashboard/`
3. Click on **"🎨 Page Heroes"**
4. You'll see a list of all page heroes

### Create a New Hero

1. Click **"Add New Hero"**
2. Select the page (Home, About, Services, etc.)
3. Fill in the content:
   - **Internal Title**: For your reference (not shown to users)
   - **Eyebrow**: Small text above headline (e.g., "Dubai • Design & Build")
   - **Headline**: Main hero text (required)
   - **Subtext**: Supporting paragraph
   - **Hero Image URL**: Cloudinary URL for background image
   - **Buttons**: JSON array of CTA buttons (see format below)
   - **Pills**: JSON array of feature text
   - **Active**: Check to display on the page
4. Click **"Create Hero"**

### Edit a Hero

1. Find the hero card in the list
2. Click **"Edit"**
3. Make your changes
4. Click **"Save Changes"**

### Delete a Hero

1. Find the hero card
2. Click **"Delete"**
3. Confirm deletion

**Note**: When a hero is deleted, the page will show default content automatically.

---

## Hero Data Format

### Buttons (JSON Array)

Buttons are defined as JSON. Each button has:
- `text`: Button label
- `url`: Where the button links to
- `style`: Either `"outline"` or `"filled"`
- `icon` (optional): FontAwesome icon class

**Example:**
```json
[
  {
    "text": "Explore Services",
    "url": "#services",
    "style": "outline"
  },
  {
    "text": "Request Consultation",
    "url": "#contact",
    "style": "filled",
    "icon": "fa-solid fa-calendar-check"
  }
]
```

### Pills (JSON Array)

Pills are simple text snippets shown as rounded badges:

**Example:**
```json
[
  "Single point of accountability",
  "Fixed milestones & transparent reporting",
  "Aftercare & facility management"
]
```

---

## How It Works

### Template Integration

The hero partial (`myApp/templates/partials/hero.html`) checks for a `hero` variable in the template context:

```django
{% if hero %}
  {# Display dynamic hero content #}
{% else %}
  {# Display default hardcoded content #}
{% endif %}
```

### View Integration

To use dynamic heroes in your views, fetch the hero and pass it to the template:

```python
from myApp.models import PageHero

def my_view(request):
    hero = PageHero.get_hero_for_page('home')  # or 'about', 'services', etc.
    
    return render(request, 'my_template.html', {
        'hero': hero,
        # ... other context
    })
```

**Already Integrated Pages:**
- ✅ Home (`/`)

**To Integrate Other Pages:**
Add the hero fetch to these views:
- `about()` view → `hero = PageHero.get_hero_for_page('about')`
- `service_index()` → `hero = PageHero.get_hero_for_page('services')`
- `projects_index()` → `hero = PageHero.get_hero_for_page('projects')`
- `insights_list()` → `hero = PageHero.get_hero_for_page('insights')`
- `contact()` → `hero = PageHero.get_hero_for_page('contact')`

---

## Model Reference

### PageHero Model

Located in `myApp/models.py`:

**Fields:**
- `page` (CharField): Which page this hero applies to (choices: home, about, services, projects, insights, contact)
- `title` (CharField): Internal title for identification
- `eyebrow` (CharField): Small text above headline
- `headline` (CharField): Main hero headline
- `subtext` (TextField): Supporting text
- `hero_image_url` (URLField): Background image URL
- `buttons` (JSONField): Array of button objects
- `pills` (JSONField): Array of pill text
- `is_active` (BooleanField): Whether to display this hero
- `created_at` (DateTimeField): Auto timestamp
- `updated_at` (DateTimeField): Auto timestamp

**Methods:**
- `get_hero_for_page(page_identifier)`: Class method to get active hero for a page

---

## URLs

The following dashboard URLs are available:

- `/dashboard/heroes/` - List all page heroes
- `/dashboard/heroes/new/` - Create a new hero
- `/dashboard/heroes/<id>/edit/` - Edit a hero
- `/dashboard/heroes/<id>/delete/` - Delete a hero

---

## Permissions

All hero management views require:
- User must be logged in
- User must be a superuser OR have admin role in their profile

Regular users and blog authors cannot access hero management.

---

## Tips & Best Practices

### Images
- Use Cloudinary URLs for hero images
- Recommended size: 1920x1080 or larger
- Use `f_auto,q_auto` in Cloudinary URLs for optimization
- Test images on different screen sizes

### Headlines
- Keep headlines under 80 characters for best display
- Use active, benefit-focused language
- Consider mobile display (text wraps on small screens)

### Buttons
- Use 1-2 buttons maximum for clarity
- Primary action = "filled" style
- Secondary action = "outline" style
- Make URLs descriptive (use anchors like `#services`)

### Pills
- Keep 2-4 pills for best display
- Use short, punchy phrases (3-7 words)
- Highlight key benefits or differentiators

---

## Troubleshooting

### Hero not showing up
1. Check if the hero is marked as **Active** in the dashboard
2. Verify the view is passing `hero` to the template context
3. Check browser console for JavaScript errors
4. Clear browser cache and reload

### Buttons not displaying correctly
1. Validate JSON format using a JSON validator
2. Check that `style` is either "outline" or "filled"
3. Ensure `url` and `text` fields are present

### Image not loading
1. Verify the Cloudinary URL is public
2. Test the URL directly in a browser
3. Check for CORS issues in browser console
4. Ensure URL uses HTTPS

---

## Future Enhancements

Possible improvements to consider:

- [ ] Visual editor for buttons and pills (no JSON editing)
- [ ] Image upload directly from dashboard
- [ ] Preview before save
- [ ] A/B testing support
- [ ] Schedule hero changes
- [ ] Hero templates/presets

---

## Questions?

If you encounter any issues or have questions, check:
1. Django admin logs: `/admin/`
2. Server logs for errors
3. Browser console for JavaScript issues

For development questions, refer to the Django documentation or contact your development team.

