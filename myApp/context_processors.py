# myApp/context_processors.py
from .models import Service

def nav_services(request):
    """
    Navigation data for header:
    - nav_services: lightweight list of services
    - nav_current_slug: current service slug (if on a detail route)
    - nav_detail_urlname: which URL name to use when linking to details
    """
    services_qs = (
        Service.objects
        .only("id", "title", "slug", "eyebrow")
        .order_by("title")
    )
    services = list(services_qs)

    # Infer current view and slug
    rm = getattr(request, "resolver_match", None)
    current_slug = None
    detail_urlname = "service_detail"  # canonical default

    if rm:
        current_slug = rm.kwargs.get("slug")
        # If you’re looking at preview, keep menu links on preview
        if rm.view_name == "service_detail_preview":
            detail_urlname = "service_detail_preview"

    return {
        "nav_services": services,
        "nav_current_slug": current_slug,
        "nav_detail_urlname": detail_urlname,
    }
