from __future__ import annotations

import json
import logging
from typing import Iterable, Mapping, Any

import requests
from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import escape
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch

from .models import (
    Service,
    ServiceFeature,
    ServiceEditorialImage,
    ServiceProjectImage,
    ServiceCapability,
    ServiceProcessStep,
    ServiceMetric,
    ServiceFAQ,
    ServicePartnerBrand,
    ServiceTestimonial,
    Insight,
)

# -----------------------------
# Home
# -----------------------------
def home(request):
    return render(request, "index.html")

# (optional) your static test page – keep if you still need it
def landscape(request):
    return render(request, "services/landscape_Detail.html")

# -----------------------------
# Services index (simple cards)
# -----------------------------
def service_index(request):
    services = (
        Service.objects.only(
            "id", "title", "slug", "hero_headline", "hero_media_url",
            "seo_meta_title", "seo_meta_description"
        )
        .order_by("title")
    )
    return render(request, "services/index.html", {"services": services})

# -----------------------------
# Dynamic Service detail (prefetch + pairs)
# -----------------------------
from django.db.models import Prefetch

# -----------------------------
# Dynamic Service detail (prefetch + pairs)
# -----------------------------
def service_detail(request, slug):
    service = get_object_or_404(
        Service.objects.only(
            "id","slug","title","eyebrow",
            "hero_headline","hero_subcopy","hero_media_url",
            "stat_projects","stat_years","stat_specialists",
            "pinned_heading","pinned_title","pinned_body_1","pinned_body_2",
            "insights_heading","insights_subcopy",
            "seo_meta_title","seo_meta_description","canonical_path",
        ).prefetch_related(
            Prefetch("features",
                queryset=ServiceFeature.objects.only(
                    "id","service_id","sort_order","icon_class","label"
                ).order_by("sort_order","id")),
            Prefetch("editorial_images",
                queryset=ServiceEditorialImage.objects.only(
                    "id","service_id","sort_order","image_url","caption"
                ).order_by("sort_order","id")),
            Prefetch("project_images",
                queryset=ServiceProjectImage.objects.only(
                    "id","service_id","sort_order","thumb_url","full_url","caption"
                ).order_by("sort_order","id")),
            Prefetch("capabilities",
                queryset=ServiceCapability.objects.only(
                    "id","service_id","sort_order","title","blurb","icon_class"
                ).order_by("sort_order","id")),
            Prefetch("process_steps",
                queryset=ServiceProcessStep.objects.only(
                    "id","service_id","sort_order","step_no","title","description"
                ).order_by("sort_order","step_no","id")),
            Prefetch("metrics",
                queryset=ServiceMetric.objects.only(
                    "id","service_id","sort_order","value","label"
                ).order_by("sort_order","id")),
            Prefetch("faqs",
                queryset=ServiceFAQ.objects.only(
                    "id","service_id","sort_order","question","answer"
                ).order_by("sort_order","id")),
            Prefetch("partner_brands",
                queryset=ServicePartnerBrand.objects.only(
                    "id","service_id","sort_order","name","logo_url","site_url"
                ).order_by("sort_order","id")),
            Prefetch("testimonials",
                queryset=ServiceTestimonial.objects.only(
                    "id","service_id","sort_order","author","role_company","quote","headshot_url"
                ).order_by("sort_order","id")),
            # 👇 give insights a to_attr so we can read the prefetched list directly
            Prefetch(
                "insights",
                queryset=Insight.objects.filter(published=True, published_at__lte=timezone.now())
                    .only("id","service_id","title","slug","tag","excerpt",
                          "cover_image_url","read_minutes","published_at")
                    .order_by("-published_at","-created_at"),
                to_attr="prefetched_insights",
            ),
        ),
        slug=slug,
    )

    editorial = list(service.editorial_images.all())
    ba_pairs = [(editorial[i], editorial[i+1]) for i in range(0, len(editorial) - 1, 2)]

    # 👇 use the prefetched list; slice to 4 if you want only four cards
    insights = getattr(service, "prefetched_insights", [])[:4]

    ctx = {
        "service": service,
        "ba_pairs": ba_pairs,
        "insights": insights,   # ← the missing piece
        "fallback_metrics": [
            {"value": service.stat_projects or "650+",   "label": "Projects Delivered"},
            {"value": service.stat_years or "20+ yrs",   "label": "Operating in Dubai"},
            {"value": service.stat_specialists or "1000+","label": "In-house Specialists"},
        ],
    }
    return render(request, "services/service_detail.html", ctx)


# -----------------------------
# Insight detail
# -----------------------------
def insight_detail(request, slug):
    insight = get_object_or_404(
        Insight.objects.select_related("service"),
        slug=slug, published=True
    )
    related = (
        Insight.objects
        .filter(service=insight.service, published=True)
        .exclude(id=insight.id)
        .order_by("-published_at", "-created_at")[:4]
    )
    return render(request, "insights/detail.html", {
        "insight": insight,
        "related": related,
    })



# myApp/views.py
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Service, ServiceProjectImage

def projects_index(request, service_slug=None):
    """
    Projects gallery aggregated from ServiceProjectImage.
    - Optional filter by service via /projects/<service_slug>/
    - Simple pagination with ?page=#
    """
    services = (
        Service.objects.only("id", "title", "slug")
        .order_by("title")
    )

    current_service = None
    images_qs = (
        ServiceProjectImage.objects.select_related("service")
        .only("id", "service_id", "thumb_url", "full_url", "caption", "sort_order")
        .order_by("service_id", "sort_order", "id")
    )

    if service_slug:
        current_service = get_object_or_404(services, slug=service_slug)
        images_qs = images_qs.filter(service=current_service)

    # paginate (12 per page)
    paginator = Paginator(images_qs, 12)
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        page_obj = paginator.page(1)

    meta_title = (
        f"{current_service.title} Projects | Hammer Group"
        if current_service else
        "Projects | Hammer Group"
    )
    meta_desc = (
        f"Selected work for {current_service.title} in Dubai—materials, details and delivery."
        if current_service else
        "Selected projects by Hammer Group across landscape, interiors and build—crafted with premium materials and clean execution."
    )

    ctx = {
        "services": services,
        "current_service": current_service,
        "page_obj": page_obj,
        "meta_title": meta_title,
        "meta_desc": meta_desc,
    }
    return render(request, "projects/index.html", ctx)



# myApp/views.py (append)
from django.shortcuts import render
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce

from .models import (
    Service,
    ServiceProjectImage,
    ServiceEditorialImage,
)

from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from .models import (
    Service, ServiceProjectImage, ServiceEditorialImage, ServiceFeature
)

def about(request):
    # first image per service (project → editorial → hero)
    first_proj_sq = Subquery(
        ServiceProjectImage.objects
            .filter(service=OuterRef('pk'))
            .order_by('sort_order', 'id')
            .values('full_url')[:1]
    )
    first_edit_sq = Subquery(
        ServiceEditorialImage.objects
            .filter(service=OuterRef('pk'))
            .order_by('sort_order', 'id')
            .values('image_url')[:1]
    )
    # first icon (from features) – optional but makes the list feel branded
    first_icon_sq = Subquery(
        ServiceFeature.objects
            .filter(service=OuterRef('pk'))
            .order_by('sort_order', 'id')
            .values('icon_class')[:1]
    )

    services_db = (
        Service.objects
        .filter(is_active=True)
        .order_by('sort_order', 'title')
        .annotate(_first_proj=first_proj_sq, _first_edit=first_edit_sq)
        .annotate(first_media_url=Coalesce('_first_proj', '_first_edit', 'hero_media_url'))
        .annotate(first_icon_class=first_icon_sq)
    )



    ctx = {
        "metrics": [
            {"value": "1000+", "label": "Projects Delivered"},
            {"value": "20+ yrs", "label": "Operating in Dubai"},
            {"value": "98%",   "label": "On-time Handover"},
        ],
        "services_db": services_db,
        "values": [
            {"title":"One accountable team","body":"Design, engineering and build under one roof — fewer hand-offs, faster decisions."},
            {"title":"Clear milestones","body":"Fixed phases and weekly reporting keep scope, cost and timeline visible."},
            {"title":"Materials that last","body":"We specify for UAE climate — stone, timber and systems that age well."},
        ],
        "steps": [
        {"icon": "fa-solid fa-compass-drafting", "title": "Discovery & brief",
         "body": "Lifestyle/brand analysis, constraints and budget alignment.", "step_no": 1},
        {"icon": "fa-solid fa-layer-group", "title": "Concept & 3D",
         "body": "Plans, 3D mood and material palettes for sign-off.", "step_no": 2},
        {"icon": "fa-solid fa-gears", "title": "Technical & BOQ",
         "body": "Drawings, MEP/structural coordination and cost book.", "step_no": 3},
        {"icon": "fa-solid fa-helmet-safety", "title": "Build & handover",
         "body": "Sequenced works, QA and snag-free delivery — with aftercare.", "step_no": 4},
        ],
        "leaders": [
            {"name":"Aisha Karim","role":"Head of Landscape","photo":"https://i.pravatar.cc/600?img=12","bio":"Native planting, water features and lighting that feel effortless."},
            {"name":"Omar Haddad","role":"Design Director, Interiors","photo":"https://i.pravatar.cc/600?img=28","bio":"Timeless palettes and precise detailing for calm, livable spaces."},
            {"name":"Layla Mansour","role":"Director, Joinery","photo":"https://i.pravatar.cc/600?img=47","bio":"Bespoke kitchens and wardrobes from our in-house production."},
            {"name":"Yusuf Rahman","role":"Director, Marble","photo":"https://i.pravatar.cc/600?img=31","bio":"Sourcing and finishing natural stone for signature moments."},
            {"name":"Sara Al Qasimi","role":"Head of Delivery","photo":"https://i.pravatar.cc/600?img=15","bio":"Fixed milestones and clean sites — zero surprises."},
            {"name":"Daniel Torres","role":"Engineering Lead","photo":"https://i.pravatar.cc/600?img=55","bio":"MEP and structural coordination resolved before site."},
            {"name":"Hind Al Ameeri","role":"Facility Management Lead","photo":"https://i.pravatar.cc/600?img=5","bio":"Planned maintenance, uptime and clean operations."},
            {"name":"Michael Stone","role":"Client Services","photo":"https://i.pravatar.cc/600?img=3","bio":"A single point of contact from briefing to aftercare."},
        ],
        "timeline": [
            {"year":"2005","event":"Founded in Dubai — boutique landscape studio."},
            {"year":"2010","event":"Expanded to interiors and engineering services."},
            {"year":"2016","event":"Opened 22,000 sqft joinery production facility."},
            {"year":"2020","event":"Marble division launched for custom stonework."},
            {"year":"2023","event":"Facility Management division formalized for aftercare."},
        ],
        "brands": [
            {"name":"Cosentino","logo_url":"https://dummyimage.com/240x80/eeeeee/111111&text=Cosentino","site_url":"https://www.cosentino.com/"},
            {"name":"Flos","logo_url":"https://dummyimage.com/240x80/eeeeee/111111&text=Flos","site_url":"https://www.flos.com/"},
            {"name":"Hunter","logo_url":"https://dummyimage.com/240x80/eeeeee/111111&text=Hunter","site_url":"https://www.hunterindustries.com/"},
            {"name":"Lutron","logo_url":"https://dummyimage.com/240x80/eeeeee/111111&text=Lutron","site_url":"https://www.lutron.com/"},
        ],
        "quotes": [
            {
        "quote": "Real estate construction companies may also engage in sales & marketing activities to promote their developed properties. 👍",
        "author": "Alex Jordan",
        "role": "Project Manager",
        "company": "Jordan Build Co.",
        "location": "Amman, JO",
        "stars": 5,
        "avatar_url": "https://i.pravatar.cc/600?img=5",
    },
    {
        "quote": "These services involve site analysis, feasibility studies, and estimation before construction begins.",
        "author": "Angelina Rose",
        "role": "Estimator",
        "stars": 5,
        "avatar_url": "https://i.pravatar.cc/600?img=5",
    },
    {
        "quote": "Demolition companies handle safe, controlled removal of existing structures, making way for new builds.",
        "author": "Alex Jordan",
        "role": "PM",
        "stars": 5,
        "avatar_url": "https://i.pravatar.cc/600?img=5",
    },
        ],
    }
    return render(request, "about.html", ctx)

# myApp/views.py


logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------
# Contact form (kept in views for simplicity; you can move to forms.py later)
# --------------------------------------------------------------------------------------
SERVICE_CHOICES = [
    ("General", "General Enquiry"),
    ("Landscape", "Landscape"),
    ("Interior", "Interior"),
    ("Joinery", "Joinery"),
    ("Marble", "Marble"),
    ("Facility Management", "Facility Management"),
]

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Your name"}),
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )
    phone = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+971 … (optional)"}),
    )
    service = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        required=False,
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Tell us about your project…"}),
    )

    # Optional honeypot for basic bot noise
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned = super().clean()
        # Basic honeypot check
        if cleaned.get("website"):
            raise forms.ValidationError("Spam detected.")
        return cleaned


# --------------------------------------------------------------------------------------
# Resend helper
# --------------------------------------------------------------------------------------
def send_email_resend(
    *,
    subject: str,
    to: Iterable[str],
    text: str,
    html: str,
    reply_to: str | None = None,
    tags: Mapping[str, Any] | None = None,
) -> tuple[bool, str]:
    """
    Send an email with Resend (https://resend.com).
    Returns (ok, message_or_error).
    """
    api_key = getattr(settings, "RESEND_API_KEY", None)
    sender = getattr(settings, "RESEND_FROM", getattr(settings, "DEFAULT_FROM_EMAIL", None))
    base_url = getattr(settings, "RESEND_BASE_URL", "https://api.resend.com")

    if not api_key or not sender:
        return (False, "Resend not configured: missing RESEND_API_KEY or RESEND_FROM.")

    url = f"{base_url.rstrip('/')}/emails"
    payload = {
        "from": sender,
        "to": list(to),
        "subject": subject[:300],  # keep it reasonable
        "text": text,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = [reply_to]
    if tags:
        # Resend supports custom headers/metadata via tags
        payload["tags"] = [{"name": str(k), "value": str(v)} for k, v in tags.items()]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        if resp.status_code in (200, 201, 202):
            return (True, "Sent")
        # Try to surface JSON error if present
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        logger.error("Resend error %s: %s", resp.status_code, detail)
        return (False, f"Resend error {resp.status_code}: {detail}")
    except requests.RequestException as e:
        logger.exception("Resend request failed")
        return (False, f"Resend request failed: {e}")


# --------------------------------------------------------------------------------------
# Contact view
# --------------------------------------------------------------------------------------
def _is_ajax(request: HttpRequest) -> bool:
    # Works for fetch()/XHR and HTMX too
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or bool(
        request.headers.get("HX-Request")
    )

@require_http_methods(["GET", "POST"])
def contact(request: HttpRequest) -> HttpResponse:
    """
    Renders a contact page and handles submissions.

    Settings used (set these in your environment or settings.py):
      RESEND_API_KEY        = "re_XXXX..."
      RESEND_FROM           = "Hammer <hello@yourdomain.com>"
      RESEND_BASE_URL       = "https://api.resend.com"            # optional
      CONTACT_TO_EMAIL      = "inbox@yourdomain.com"              # optional
      DEFAULT_FROM_EMAIL    = "hello@yourdomain.com"              # fallback
    """
    initial_service = request.GET.get("service")  # preselect from ?service=Interior, etc.
    initial = {"service": initial_service} if initial_service else None

    if request.method == "GET":
        form = ContactForm(initial=initial)
        return render(request, "contact.html", {"form": form})

    # POST
    form = ContactForm(request.POST)
    if not form.is_valid():
        if _is_ajax(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        messages.error(request, "Please correct the errors and try again.")
        return render(request, "contact.html", {"form": form})

    data = form.cleaned_data
    service = data.get("service") or "General"
    subject = f"[Enquiry] {service} — {data['name']}"

    # Build safe plain text (readable in any client)
    text_lines = [
        f"Name: {data['name']}",
        f"Email: {data['email']}",
        f"Phone: {data.get('phone', '')}",
        f"Service: {service}",
        "",
        "Message:",
        data["message"],
        "",
    ]
    text = "\n".join(text_lines)

    # SAFELY escape + convert newlines -> <br> for HTML version
    safe_message_html = escape(data["message"]).replace("\n", "<br>")

    html = (
        "<div style='font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;'>"
        "<h2 style='margin:0 0 12px 0;'>New enquiry</h2>"
        "<p><strong>Name:</strong> " + escape(data["name"]) + "</p>"
        "<p><strong>Email:</strong> " + escape(data["email"]) + "</p>"
        "<p><strong>Phone:</strong> " + escape(data.get("phone", "")) + "</p>"
        "<p><strong>Service:</strong> " + escape(service) + "</p>"
        "<hr style='border:none;border-top:1px solid #e5e7eb;margin:12px 0'>"
        "<p><strong>Message:</strong><br>" + safe_message_html + "</p>"
        "</div>"
    )

    to_addr = getattr(settings, "CONTACT_TO_EMAIL", getattr(settings, "DEFAULT_FROM_EMAIL", None))
    if not to_addr:
        # fall back hard to avoid silent drop
        to_addr = data["email"]

    ok, detail = send_email_resend(
        subject=subject,
        to=[to_addr],
        text=text,
        html=html,
        reply_to=data["email"],
        tags={"env": getattr(settings, "ENVIRONMENT", "prod"), "type": "contact"},
    )

    if _is_ajax(request):
        status = 200 if ok else 502
        return JsonResponse({"ok": ok, "detail": detail}, status=status)

    if ok:
        messages.success(request, "Thanks — your message is on its way. We’ll get back to you shortly.")
        # Optional: redirect to a lightweight thank-you route if you have one
        return redirect(f"{reverse('contact')}?sent=1")
    else:
        messages.error(request, "Sorry, we couldn’t send your message. Please try again in a moment.")
        return render(request, "contact.html", {"form": form})
