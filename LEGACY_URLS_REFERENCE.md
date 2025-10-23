# Legacy URLs Reference - Hammer Services

This document lists all the legacy URLs from the old website that have been configured to work with the new Django application.

## Main Legacy URLs

| Legacy URL | Redirects To | Description |
|------------|--------------|-------------|
| `https://www.hammer-services.com/landscape` | `landscape-design-build` service | Landscape design and build service |
| `https://www.hammer-services.com/interior` | `interior-design-build` service | Interior design and build service |
| `https://www.hammer-services.com/villas` | Home page | Villa projects showcase |
| `https://www.hammer-services.com/facility` | `facility-management` service | Facility management and aftercare |
| `https://www.hammer-services.com/aboutus` | About page | Company information |
| `https://www.hammer-services.com/projects` | Projects index | All projects showcase |

## Service-Specific Legacy URLs

| Legacy URL | Redirects To | Description |
|------------|--------------|-------------|
| `https://www.hammer-services.com/services/landscaping/` | `landscape-design-build` service | Landscape services |
| `https://www.hammer-services.com/services/maintenance/` | `facility-management` service | Facility maintenance services |
| `https://www.hammer-services.com/services/swimming-pools/` | `landscape-design-build` service | Pool and landscape services |
| `https://www.hammer-services.com/services/home-renovation/` | Home page | Home renovation projects |
| `https://www.hammer-services.com/services/commercial-fit-out/` | `interior-design-build` service | Commercial interior services |

## Long-Form Legacy URLs

| Legacy URL | Redirects To | Description |
|------------|--------------|-------------|
| `https://www.hammer-services.com/interior/residential-fit-out-company-in-dubai/` | `interior-design-build` service | Residential fit-out services |
| `https://www.hammer-services.com/landscape/landscape-design-development-company/` | `landscape-design-build` service | Landscape design services |

## URL Configuration Details

### Service Mappings
- **Landscape Services**: `landscape-design-build` service
- **Interior Services**: `interior-design-build` service  
- **Facility Services**: `facility-management` service
- **General Pages**: Home, About, Projects

### Technical Implementation
- All legacy URLs are handled by dedicated legacy views
- URLs are configured in `myApp/urls.py`
- Legacy views redirect to the appropriate service detail pages
- Specific URL patterns are placed before generic patterns to avoid conflicts

### SEO Considerations
- All redirects maintain the original URL structure
- No 404 errors for legacy URLs
- Proper service content is served for each legacy URL
- Canonical URLs are maintained for SEO

## Testing Checklist

- [ ] `/landscape` - Should show landscape service page
- [ ] `/interior` - Should show interior service page  
- [ ] `/villas` - Should show home page
- [ ] `/facility` - Should show facility management service page
- [ ] `/aboutus` - Should show about page
- [ ] `/projects` - Should show projects index
- [ ] `/services/landscaping/` - Should show landscape service page
- [ ] `/services/maintenance/` - Should show facility management service page
- [ ] `/services/swimming-pools/` - Should show landscape service page
- [ ] `/services/home-renovation/` - Should show home page
- [ ] `/services/commercial-fit-out/` - Should show interior service page
- [ ] `/interior/residential-fit-out-company-in-dubai/` - Should show interior service page
- [ ] `/landscape/landscape-design-development-company/` - Should show landscape service page

## Notes

- All URLs work with and without trailing slashes
- Legacy URLs are preserved for backward compatibility
- No changes needed to existing links or bookmarks
- All URLs redirect to the appropriate content on the new site structure

---
*Last updated: $(date)*
*Generated from Django URL configuration in myApp/urls.py*
