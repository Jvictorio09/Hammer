# Complete URLs Reference - Hammer Services Website

This document provides a comprehensive list of ALL URLs available on the Hammer Services website, including public pages, legacy URLs, and admin/dashboard URLs.

## 🌐 Public Website URLs

### Home & Main Pages
| URL | Description | Access Level |
|-----|--------------|--------------|
| [https://www.hammer-services.com/](https://www.hammer-services.com/) | Home page | Public |
| [https://www.hammer-services.com/villas](https://www.hammer-services.com/villas) | Villa projects showcase | Public |
| [https://www.hammer-services.com/about/](https://www.hammer-services.com/about/) | About page | Public |
| [https://www.hammer-services.com/contact/](https://www.hammer-services.com/contact/) | Contact page | Public |

### Services
| URL | Description | Access Level |
|-----|--------------|--------------|
| [https://www.hammer-services.com/services/](https://www.hammer-services.com/services/) | Services index page | Public |
| [https://www.hammer-services.com/services/landscape-design-build/](https://www.hammer-services.com/services/landscape-design-build/) | Landscape Design & Build | Public |
| [https://www.hammer-services.com/services/interior-design-build/](https://www.hammer-services.com/services/interior-design-build/) | Interior Design & Build | Public |
| [https://www.hammer-services.com/services/facility-management/](https://www.hammer-services.com/services/facility-management/) | Facility Management & Aftercare | Public |

### Content Pages
| URL | Description | Access Level |
|-----|--------------|--------------|
| [https://www.hammer-services.com/insights/](https://www.hammer-services.com/insights/) | Blog/insights list page | Public |
| [https://www.hammer-services.com/insights/](https://www.hammer-services.com/insights/) | Individual insight/blog post | Public |
| [https://www.hammer-services.com/case-studies/](https://www.hammer-services.com/case-studies/) | Individual case study detail | Public |
| [https://www.hammer-services.com/projects/](https://www.hammer-services.com/projects/) | All projects showcase | Public |
| [https://www.hammer-services.com/projects/](https://www.hammer-services.com/projects/) | Projects filtered by service | Public |
| [https://www.hammer-services.com/team/](https://www.hammer-services.com/team/) | Individual team member profile | Public |

### Legacy URLs (Backward Compatibility)
| URL | Redirects To | Description |
|-----|-------------|-------------|
| [https://www.hammer-services.com/landscape](https://www.hammer-services.com/landscape) | `landscape-design-build` service | Legacy landscape URL |
| [https://www.hammer-services.com/landscape/](https://www.hammer-services.com/landscape/) | `landscape-design-build` service | Legacy landscape URL |
| [https://www.hammer-services.com/interior](https://www.hammer-services.com/interior) | `interior-design-build` service | Legacy interior URL |
| [https://www.hammer-services.com/interior/](https://www.hammer-services.com/interior/) | `interior-design-build` service | Legacy interior URL |
| [https://www.hammer-services.com/facility](https://www.hammer-services.com/facility) | `facility-management` service | Legacy facility URL |
| [https://www.hammer-services.com/facility/](https://www.hammer-services.com/facility/) | `facility-management` service | Legacy facility URL |
| [https://www.hammer-services.com/aboutus](https://www.hammer-services.com/aboutus) | About page | Legacy about URL |
| [https://www.hammer-services.com/aboutus/](https://www.hammer-services.com/aboutus/) | About page | Legacy about URL |
| [https://www.hammer-services.com/blogs/](https://www.hammer-services.com/blogs/) | Insights list page | Legacy blog URL |
| [https://www.hammer-services.com/landscaping/](https://www.hammer-services.com/landscaping/) | `landscape-design-build` service | Legacy landscaping URL |

### Legacy Service URLs
| URL | Redirects To | Description |
|-----|-------------|-------------|
| [https://www.hammer-services.com/services/landscaping/](https://www.hammer-services.com/services/landscaping/) | `landscape-design-build` service | Legacy landscaping service |
| [https://www.hammer-services.com/services/landscape/](https://www.hammer-services.com/services/landscape/) | `landscape-design-build` service | Legacy landscape service |
| [https://www.hammer-services.com/services/maintenance/](https://www.hammer-services.com/services/maintenance/) | `facility-management` service | Legacy maintenance service |
| [https://www.hammer-services.com/services/swimming-pools/](https://www.hammer-services.com/services/swimming-pools/) | `landscape-design-build` service | Legacy pool service |
| [https://www.hammer-services.com/services/home-renovation/](https://www.hammer-services.com/services/home-renovation/) | Home page | Legacy renovation service |
| [https://www.hammer-services.com/services/commercial-fit-out/](https://www.hammer-services.com/services/commercial-fit-out/) | `interior-design-build` service | Legacy commercial service |

### Legacy Long-Form URLs
| URL | Redirects To | Description |
|-----|-------------|-------------|
| [https://www.hammer-services.com/interior/residential-fit-out-company-in-dubai/](https://www.hammer-services.com/interior/residential-fit-out-company-in-dubai/) | `interior-design-build` service | SEO-optimized interior URL |
| [https://www.hammer-services.com/landscape/landscape-design-development-company/](https://www.hammer-services.com/landscape/landscape-design-development-company/) | `landscape-design-build` service | SEO-optimized landscape URL |

## 🔐 Authentication URLs

| URL | Description | Access Level |
|-----|-------------|--------------|
| `/accounts/login/` | User login page | Public |
| `/accounts/logout/` | User logout (redirects to home) | Public |

## 🛠️ Admin & Dashboard URLs

### Django Admin
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/admin/` | Django admin interface | Admin only |

### Dashboard Home
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/` | Dashboard home page | Authenticated users |

### Services Management
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/services/` | List all services | Authenticated users |
| `/dashboard/services/new/` | Create new service | Authenticated users |
| `/dashboard/services/<id>/edit/` | Edit service | Authenticated users |
| `/dashboard/services/<id>/delete/` | Delete service | Authenticated users |

### Insights/Blog Management
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/insights/` | List all insights | Authenticated users |
| `/dashboard/insights/new/` | Create new insight | Authenticated users |
| `/dashboard/insights/<id>/edit/` | Edit insight | Authenticated users |
| `/dashboard/insights/<id>/delete/` | Delete insight | Authenticated users |
| `/dashboard/insights/<id>/toggle-active/` | Toggle insight active status | Authenticated users |
| `/dashboard/insights/import/` | Import insights from HTML | Authenticated users |

### Team Management
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/team/` | List all team members | Authenticated users |
| `/dashboard/team/new/` | Create new team member | Authenticated users |
| `/dashboard/team/<id>/edit/` | Edit team member | Authenticated users |
| `/dashboard/team/<id>/delete/` | Delete team member | Authenticated users |

### User Management (Admin Only)
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/users/` | List all users | Admin only |
| `/dashboard/users/new/` | Create new user | Admin only |
| `/dashboard/users/<id>/edit/` | Edit user | Admin only |
| `/dashboard/users/<id>/delete/` | Delete user | Admin only |

## 📁 Gallery & Media Management

### Gallery API
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/gallery/api/images/` | Get gallery images | Authenticated users |
| `/dashboard/gallery/api/upload/` | Upload images to gallery | Authenticated users |
| `/dashboard/gallery/api/delete/` | Delete images from gallery | Authenticated users |

### Google Drive Integration
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/dashboard/gallery/api/google-drive/upload/` | Upload to Google Drive | Authenticated users |
| `/dashboard/gallery/api/google-drive/bulk-upload/` | Bulk upload to Google Drive | Authenticated users |

### Editor Integration
| URL | Description | Access Level |
|-----|-------------|--------------|
| `/u/editor-image/` | Editor.js image upload endpoint | Authenticated users |

## 🧪 Development & Testing

| URL | Description | Access Level |
|-----|-------------|--------------|
| `/test-look/` | Static test page | Public |

## 📋 URL Testing Checklist

### Public URLs
- [ ] [https://www.hammer-services.com/](https://www.hammer-services.com/) - Home page loads
- [ ] [https://www.hammer-services.com/services/](https://www.hammer-services.com/services/) - Services index loads
- [ ] [https://www.hammer-services.com/services/landscape-design-build/](https://www.hammer-services.com/services/landscape-design-build/) - Landscape service loads
- [ ] [https://www.hammer-services.com/services/interior-design-build/](https://www.hammer-services.com/services/interior-design-build/) - Interior service loads
- [ ] [https://www.hammer-services.com/services/facility-management/](https://www.hammer-services.com/services/facility-management/) - Facility service loads
- [ ] [https://www.hammer-services.com/insights/](https://www.hammer-services.com/insights/) - Insights list loads
- [ ] [https://www.hammer-services.com/projects/](https://www.hammer-services.com/projects/) - Projects page loads
- [ ] [https://www.hammer-services.com/about/](https://www.hammer-services.com/about/) - About page loads
- [ ] [https://www.hammer-services.com/contact/](https://www.hammer-services.com/contact/) - Contact page loads

### Legacy URLs
- [ ] [https://www.hammer-services.com/landscape](https://www.hammer-services.com/landscape) - Redirects to landscape service
- [ ] [https://www.hammer-services.com/interior](https://www.hammer-services.com/interior) - Redirects to interior service
- [ ] [https://www.hammer-services.com/facility](https://www.hammer-services.com/facility) - Redirects to facility service
- [ ] [https://www.hammer-services.com/aboutus](https://www.hammer-services.com/aboutus) - Redirects to about page
- [ ] [https://www.hammer-services.com/projects](https://www.hammer-services.com/projects) - Redirects to projects page
- [ ] [https://www.hammer-services.com/services/landscaping/](https://www.hammer-services.com/services/landscaping/) - Redirects to landscape service
- [ ] [https://www.hammer-services.com/services/maintenance/](https://www.hammer-services.com/services/maintenance/) - Redirects to facility service
- [ ] [https://www.hammer-services.com/services/swimming-pools/](https://www.hammer-services.com/services/swimming-pools/) - Redirects to landscape service
- [ ] [https://www.hammer-services.com/services/commercial-fit-out/](https://www.hammer-services.com/services/commercial-fit-out/) - Redirects to interior service

### Authentication
- [ ] `/accounts/login/` - Login page loads
- [ ] `/accounts/logout/` - Logout redirects to home

### Dashboard (Requires Login)
- [ ] `/dashboard/` - Dashboard home loads
- [ ] `/dashboard/services/` - Services management loads
- [ ] `/dashboard/insights/` - Insights management loads
- [ ] `/dashboard/team/` - Team management loads

## 🔧 Technical Notes

### URL Pattern Order
- Specific legacy URLs are placed before generic patterns
- Service detail URLs use slug parameters
- Dashboard URLs require authentication
- Admin URLs require admin privileges

### SEO Considerations
- All legacy URLs maintain proper redirects
- Canonical URLs are preserved
- No 404 errors for legacy URLs
- Proper meta tags and descriptions

### Security
- Dashboard URLs require authentication
- Admin URLs require admin privileges
- API endpoints are protected
- File uploads are secured

---
*Last updated: $(date)*
*Generated from Django URL configuration in myApp/urls.py and myProject/urls.py*
