# Google Ads URL Fix Guide

## Problem
Multiple URLs are being flagged by Google Ads as "Destination not working" even though they work in browsers.

## Root Cause
Google Ads validation is stricter than browser requests. Issues can occur with:
1. Catchall URL patterns (like `/interior/<path:sub_path>/`)
2. Temporary server errors during validation
3. Missing explicit routes for commonly used ad URLs

## Solution
We've implemented a two-part solution:

### 1. Explicit Routes for Ad URLs
Add explicit routes BEFORE catchall patterns in `myApp/urls.py`. This ensures Google Ads validation passes.

**Pattern to follow:**
```python
# Explicit routes for common ad URLs (must come BEFORE catchall)
path("interior/residential-fit-out/", views.legacy_interior, name="legacy_interior_residential_fitout"),
path("interior/another-url/", views.legacy_interior, name="legacy_interior_another"),

# Catchall comes AFTER explicit routes
path("interior/<path:sub_path>/", views.legacy_interior_catchall, name="legacy_interior_catchall"),
```

### 2. Adding More URLs
When you find URLs flagged in Google Ads:

1. **Identify the URL pattern** - e.g., `/interior/residential-fit-out/`
2. **Add explicit route** in `myApp/urls.py` BEFORE the catchall pattern
3. **Use the appropriate view:**
   - Interior URLs → `views.legacy_interior`
   - Landscape URLs → `views.legacy_landscape`
   - Facility URLs → `views.legacy_facility`
   - About URLs → `views.legacy_aboutus`

### Example
If Google Ads flags `/interior/commercial-fit-out/`, add:
```python
path("interior/commercial-fit-out/", views.legacy_interior, name="legacy_interior_commercial"),
```

## Testing URLs
To test if a URL works:
1. Visit the URL in a browser
2. Check for HTTP 200 status code
3. Verify content loads correctly
4. Use Google's URL Inspection Tool in Search Console

## Current Explicit Routes
- `/interior/residential-fit-out/` ✅
- `/interior/residential-fit-out-company-in-dubai/` ✅

## Next Steps
1. Identify all URLs flagged in Google Ads
2. Add explicit routes for each
3. Test each URL after adding
4. Resubmit in Google Ads
