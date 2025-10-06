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
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from functools import wraps
from django.core.files.storage import default_storage
from bs4 import BeautifulSoup
import uuid

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
    ContentVersion,
    MediaAsset,
    InsightAuditLog,
)
from .forms import ServiceForm, InsightForm, ServiceCapabilityFormSet, ServiceEditorialImageFormSet, ServiceProjectImageFormSet, CaseStudyFormSet

# -----------------------------
# Utility Functions
# -----------------------------

def get_client_ip(request):
    """Get the client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def blog_author_required(view_func):
    """Decorator to ensure user is a blog author or admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check if user is admin or blog author
        if hasattr(request.user, 'profile'):
            if not (request.user.profile.is_admin or request.user.profile.is_blog_author):
                raise PermissionDenied("You don't have permission to access this page.")
        elif not request.user.is_superuser:
            raise PermissionDenied("You don't have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to ensure user is an admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check if user is admin
        if hasattr(request.user, 'profile'):
            if not request.user.profile.is_admin:
                raise PermissionDenied("You don't have permission to access this page.")
        elif not request.user.is_superuser:
            raise PermissionDenied("You don't have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def html_to_editorjs_blocks(html_content):
    """
    Convert HTML content to Editor.js blocks format.
    """
    if not html_content or not html_content.strip():
        return {
            "time": int(timezone.now().timestamp() * 1000),
            "blocks": [],
            "version": "2.28.2"
        }
    
    soup = BeautifulSoup(html_content, 'html.parser')
    blocks = []
    
    def process_element(element):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            text = element.get_text().strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {
                        "text": text,
                        "level": level
                    }
                })
        
        elif element.name == 'blockquote':
            text = element.get_text().strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "quote",
                    "data": {
                        "text": text,
                        "caption": ""
                    }
                })
        
        elif element.name == 'ul':
            items = [li.get_text().strip() for li in element.find_all('li')]
            if items:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "list",
                    "data": {
                        "style": "unordered",
                        "items": items
                    }
                })
        
        elif element.name == 'ol':
            items = [li.get_text().strip() for li in element.find_all('li')]
            if items:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "list",
                    "data": {
                        "style": "ordered",
                        "items": items
                    }
                })
        
        elif element.name == 'p':
            text = element.get_text().strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "paragraph",
                    "data": {
                        "text": text
                    }
                })
        
        else:
            # For other elements, treat as paragraph
            text = element.get_text().strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "paragraph",
                    "data": {
                        "text": text
                    }
                })
    
    # Process all direct children of body
    for element in soup.body.find_all(recursive=False):
        process_element(element)
    
    return {
        "time": int(timezone.now().timestamp() * 1000),
        "blocks": blocks,
        "version": "2.28.2"
    }

# -----------------------------
# Home
# -----------------------------


# myApp/views.py (snippet)
from django.shortcuts import render
from .models import Service, CaseStudy

def home(request):
    services = Service.objects.filter(is_active=True).order_by("sort_order", "title")

    # Choose the first featured case study; fallback to any case study; fallback to None.
    featured_cs = (
        CaseStudy.objects.select_related("service")
        .filter(is_featured=True)
        .order_by("sort_order", "title")
        .first()
        or CaseStudy.objects.select_related("service").order_by("sort_order", "title").first()
    )

    # Optional: build filter labels from service titles
    filters = ["All"] + list(services.values_list("title", flat=True))

    return render(request, "index.html", {
        "services": services,
        "featured_cs": featured_cs,
        "project_filters": filters,
    })


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
                queryset=Insight.objects.filter(published=True, is_active=True, published_at__lte=timezone.now())
                    .select_related("author")
                    .only("id","service_id","title","slug","tag","excerpt",
                          "cover_image_url","read_minutes","published_at","author","created_at")
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
        Insight.objects.select_related("service", "author"),
        slug=slug, published=True, is_active=True
    )
    related = (
        Insight.objects
        .filter(service=insight.service, published=True, is_active=True)
        .select_related("author")
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


# myApp/views.py (append / modify your about view)
from django.shortcuts import render
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from .models import (
    Service, ServiceProjectImage, ServiceEditorialImage, ServiceFeature,
    TeamMember,  # <-- ADD
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

    # NEW: pull leaders from DB (featured + active)
    leaders_qs = (
        TeamMember.objects
        .filter(is_active=True, is_featured=True)
        .order_by('sort_order', 'id')[:16]
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
            {"icon":"fa-solid fa-compass-drafting","title":"Discovery & brief","body":"Lifestyle/brand analysis, constraints and budget alignment.","step_no":1},
            {"icon":"fa-solid fa-layer-group","title":"Concept & 3D","body":"Plans, 3D mood and material palettes for sign-off.","step_no":2},
            {"icon":"fa-solid fa-gears","title":"Technical & BOQ","body":"Drawings, MEP/structural coordination and cost book.","step_no":3},
            {"icon":"fa-solid fa-helmet-safety","title":"Build & handover","body":"Sequenced works, QA and snag-free delivery — with aftercare.","step_no":4},
        ],
        # Replace the hardcoded list with the queryset
        "leaders": [
            {"name": p.name, "role": p.role, "photo": (p.photo_card or ""), "bio": p.bio, "url": p.get_absolute_url()}
            for p in leaders_qs
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
            {"quote":"Real estate construction companies may also engage in sales & marketing activities to promote their developed properties. 👍","author":"Alex Jordan","role":"Project Manager","company":"Jordan Build Co.","location":"Amman, JO","stars":5,"avatar_url":"https://i.pravatar.cc/600?img=5"},
            {"quote":"These services involve site analysis, feasibility studies, and estimation before construction begins.","author":"Angelina Rose","role":"Estimator","stars":5,"avatar_url":"https://i.pravatar.cc/600?img=5"},
            {"quote":"Demolition companies handle safe, controlled removal of existing structures, making way for new builds.","author":"Alex Jordan","role":"PM","stars":5,"avatar_url":"https://i.pravatar.cc/600?img=5"},
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


# myApp/views.py
from django.shortcuts import get_object_or_404, render
from .models import TeamMember

def team_detail(request, slug):
    person = get_object_or_404(TeamMember, slug=slug, is_active=True)
    return render(request, "team/detail.html", {"person": person})


# --------------------------------------------------------------------------------------
# Client Dashboard (Services + Insights CRUD)
# --------------------------------------------------------------------------------------

@login_required
def dashboard_home(request):
    # Redirect Blog Authors directly to insights since they can't access other sections
    if hasattr(request.user, 'profile') and request.user.profile.is_blog_author and not request.user.profile.is_admin:
        return redirect('dashboard_insights_list')
    return render(request, "dashboard/home.html")


# ---- Services CRUD ----
@login_required
def dashboard_services_list(request):
    services = Service.objects.order_by("sort_order", "title")
    return render(request, "dashboard/services_list.html", {"services": services})


@login_required
def dashboard_service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        capability_formset = ServiceCapabilityFormSet(request.POST, prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(request.POST, prefix='images')
        project_image_formset = ServiceProjectImageFormSet(request.POST, prefix='project_images')
        case_study_formset = CaseStudyFormSet(request.POST, prefix='case_studies')
        
        if form.is_valid() and capability_formset.is_valid() and image_formset.is_valid() and project_image_formset.is_valid() and case_study_formset.is_valid():
            service = form.save()
            capability_formset.instance = service
            capability_formset.save()
            image_formset.instance = service
            image_formset.save()
            project_image_formset.instance = service
            project_image_formset.save()
            case_study_formset.instance = service
            case_study_formset.save()
            return redirect(service.get_absolute_url())
    else:
        form = ServiceForm()
        capability_formset = ServiceCapabilityFormSet(prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(prefix='images')
        project_image_formset = ServiceProjectImageFormSet(prefix='project_images')
        case_study_formset = CaseStudyFormSet(prefix='case_studies')
    
    return render(request, "dashboard/service_form.html", {
        "form": form, 
        "capability_formset": capability_formset,
        "image_formset": image_formset,
        "project_image_formset": project_image_formset,
        "case_study_formset": case_study_formset,
        "mode": "create"
    })


@login_required
def dashboard_service_edit(request, pk: int):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        capability_formset = ServiceCapabilityFormSet(request.POST, instance=service, prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(request.POST, instance=service, prefix='images')
        project_image_formset = ServiceProjectImageFormSet(request.POST, instance=service, prefix='project_images')
        case_study_formset = CaseStudyFormSet(request.POST, instance=service, prefix='case_studies')
        
        if form.is_valid() and capability_formset.is_valid() and image_formset.is_valid() and project_image_formset.is_valid() and case_study_formset.is_valid():
            form.save()
            capability_formset.save()
            image_formset.save()
            project_image_formset.save()
            case_study_formset.save()
            return redirect("dashboard_services_list")
    else:
        form = ServiceForm(instance=service)
        capability_formset = ServiceCapabilityFormSet(instance=service, prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(instance=service, prefix='images')
        project_image_formset = ServiceProjectImageFormSet(instance=service, prefix='project_images')
        case_study_formset = CaseStudyFormSet(instance=service, prefix='case_studies')
    
    return render(request, "dashboard/service_form.html", {
        "form": form, 
        "capability_formset": capability_formset,
        "image_formset": image_formset,
        "project_image_formset": project_image_formset,
        "case_study_formset": case_study_formset,
        "mode": "edit", 
        "service": service
    })


@login_required
def dashboard_service_delete(request, pk: int):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        service.delete()
        return redirect("dashboard_services_list")
    return render(request, "dashboard/confirm_delete.html", {"object": service, "type": "Service"})


# ---- Insights CRUD ----
@blog_author_required
def dashboard_insights_list(request):
    insights = Insight.objects.select_related("service", "author").order_by("-published_at", "-created_at")
    return render(request, "dashboard/insights_list.html", {"insights": insights})


@blog_author_required
def dashboard_insight_create(request):
    if request.method == "POST":
        form = InsightForm(request.POST, request.FILES)
        if form.is_valid():
            insight = form.save(commit=False)
            # Handle blocks field from Editor.js
            try:
                blocks_data = json.loads(request.POST.get("blocks") or "{}")
                insight.blocks = blocks_data
            except json.JSONDecodeError:
                pass  # Keep empty blocks if JSON is invalid
            
            # Set author and published_at
            insight.author = request.user
            if insight.published and not insight.published_at:
                insight.published_at = timezone.now()
            
            insight.save()
            
            # Create version snapshot
            try:
                ContentVersion.objects.create(insight=insight, data=insight.blocks or {})
                stale = insight.versions.order_by("-created_at")[10:]
                if stale:
                    ContentVersion.objects.filter(pk__in=[v.pk for v in stale]).delete()
            except Exception:
                pass
            
            messages.success(request, "Insight created successfully.")
            return redirect("dashboard_insight_edit", pk=insight.pk)
    else:
        # Pre-populate service if provided in URL
        initial_data = {}
        service_id = request.GET.get('service')
        if service_id:
            try:
                service = Service.objects.get(pk=service_id)
                initial_data['service'] = service
            except Service.DoesNotExist:
                pass
        form = InsightForm(initial=initial_data)
    
    # Prepare empty blocks data for new insights
    blocks_json = "{}"
    
    return render(request, "dashboard/insight_form.html", {
        "form": form, 
        "mode": "create",
        "blocks_json": blocks_json
    })


@blog_author_required
def dashboard_insight_edit(request, pk: int):
    insight = get_object_or_404(Insight, pk=pk)
    
    # Convert HTML body to blocks if needed
    if insight.body and not insight.blocks:
        print(f"DEBUG: Converting HTML to blocks for insight: {insight.title}")
        blocks_data = html_to_editorjs_blocks(insight.body)
        insight.blocks = blocks_data
        insight.save()
        print(f"DEBUG: Converted HTML to {len(blocks_data.get('blocks', []))} blocks")
    
    if request.method == "POST":
        form = InsightForm(request.POST, request.FILES, instance=insight)
        if form.is_valid():
            obj = form.save(commit=False)
            # Handle blocks field from Editor.js
            blocks_json = request.POST.get("blocks", "{}")
            print(f"DEBUG: Received blocks JSON: {blocks_json[:100]}...")  # Debug line
            
            try:
                blocks_data = json.loads(blocks_json)
                obj.blocks = blocks_data
                print(f"DEBUG: Parsed blocks data: {len(blocks_data.get('blocks', []))} blocks")  # Debug line
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}")  # Debug line
                pass  # Keep existing blocks if JSON is invalid
            
            # Set required fields with defaults if not provided
            if not obj.slug:
                from django.utils.text import slugify
                obj.slug = slugify(obj.title)[:220]
            if not obj.read_minutes:
                obj.read_minutes = 4
            if not obj.service_id:
                # Set a default service or make it optional
                from .models import Service
                default_service = Service.objects.first()
                if default_service:
                    obj.service = default_service
            
            # Set published_at if published is True and not already set
            if obj.published and not obj.published_at:
                obj.published_at = timezone.now()
            
            obj.save()
            print(f"DEBUG: Saved insight with blocks: {obj.blocks}")  # Debug line
            
            # Create version snapshot
            try:
                ContentVersion.objects.create(insight=obj, data=obj.blocks or {})
                stale = obj.versions.order_by("-created_at")[10:]
                if stale:
                    ContentVersion.objects.filter(pk__in=[v.pk for v in stale]).delete()
            except Exception:
                pass
            
            messages.success(request, "Insight updated successfully.")
            return redirect("dashboard_insight_edit", pk=obj.pk)
        else:
            print(f"DEBUG: Form errors: {form.errors}")  # Debug line
    else:
        form = InsightForm(instance=insight)
    
    # Prepare blocks data for template
    blocks_json = json.dumps(insight.blocks) if insight.blocks else "{}"
    
    return render(request, "dashboard/insight_form.html", {
        "form": form, 
        "mode": "edit", 
        "insight": insight,
        "blocks_json": blocks_json
    })


@require_POST
@login_required
def editor_image_upload(request):
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("No file provided")
    name = default_storage.save(f"editor/{f.name}", f)
    secure_url = default_storage.url(name)
    # Prefer lightweight delivery variant for web use
    web_url = secure_url
    if "/upload/" in secure_url:
        web_url = secure_url.replace("/upload/", "/upload/f_auto,q_auto/")
    return JsonResponse({"url": secure_url, "web_url": web_url})


@blog_author_required
def dashboard_insight_delete(request, pk: int):
    insight = get_object_or_404(Insight, pk=pk)
    if request.method == "POST":
        # Create audit log before deletion
        InsightAuditLog.objects.create(
            action='delete',
            insight_id=insight.id,
            insight_slug=insight.slug,
            insight_title=insight.title,
            actor=request.user,
            actor_username=request.user.username,
            actor_email=request.user.email,
            ip_address=get_client_ip(request),
            metadata={
                'service_title': insight.service.title,
                'service_slug': insight.service.slug,
            }
        )
        
        insight.delete()
        messages.success(request, f"Insight '{insight.title}' has been deleted. Audit log created.")
        return redirect("dashboard_insights_list")
    return render(request, "dashboard/confirm_delete.html", {"object": insight, "type": "Insight"})


@admin_required
@require_POST
def dashboard_insight_toggle_active(request, pk: int):
    """Toggle insight active status (admin only)"""
    insight = get_object_or_404(Insight, pk=pk)
    
    # Toggle the active status
    old_status = insight.is_active
    insight.is_active = not insight.is_active
    insight.save()
    
    # Create audit log
    action = 'activate' if insight.is_active else 'deactivate'
    InsightAuditLog.objects.create(
        action=action,
        insight_id=insight.id,
        insight_slug=insight.slug,
        insight_title=insight.title,
        actor=request.user,
        actor_username=request.user.username,
        actor_email=request.user.email,
        ip_address=get_client_ip(request),
        metadata={
            'service_title': insight.service.title,
            'service_slug': insight.service.slug,
            'previous_status': old_status,
            'new_status': insight.is_active,
        }
    )
    
    status_text = "activated" if insight.is_active else "deactivated"
    messages.success(request, f"Insight '{insight.title}' has been {status_text}. Audit log created.")
    return redirect("dashboard_insights_list")


@blog_author_required
def dashboard_insight_import_html(request):
    """
    Import function to convert HTML body content to Editor.js blocks format.
    """
    if request.method == "POST":
        insight_id = request.POST.get('insight_id')
        if insight_id:
            try:
                insight = Insight.objects.get(pk=insight_id)
                if insight.body and not insight.blocks:
                    # Convert HTML body to blocks
                    blocks_data = html_to_editorjs_blocks(insight.body)
                    insight.blocks = blocks_data
                    insight.save()
                    messages.success(request, f"Successfully converted HTML to blocks for '{insight.title}'")
                else:
                    messages.info(request, f"Insight '{insight.title}' already has blocks or no body content")
            except Insight.DoesNotExist:
                messages.error(request, "Insight not found")
        else:
            # Convert all insights with HTML body but no blocks
            insights_to_convert = Insight.objects.filter(
                body__isnull=False
            ).exclude(body='').filter(
                blocks={}
            )
            
            converted_count = 0
            for insight in insights_to_convert:
                blocks_data = html_to_editorjs_blocks(insight.body)
                insight.blocks = blocks_data
                insight.save()
                converted_count += 1
            
            messages.success(request, f"Successfully converted {converted_count} insights from HTML to blocks")
        
        return redirect("dashboard_insights_list")
    
    # Show insights that need conversion
    insights_needing_conversion = Insight.objects.filter(
        body__isnull=False
    ).exclude(body='').filter(
        blocks={}
    )
    
    return render(request, "dashboard/insight_import.html", {
        "insights": insights_needing_conversion
    })


@login_required
def gallery_api_images(request):
    """API endpoint to fetch gallery images for the modal"""
    images = MediaAsset.objects.filter(is_active=True).select_related('album').order_by('-created_at')
    
    image_data = []
    for asset in images:
        image_data.append({
            'id': asset.id,
            'title': asset.title,
            'secure_url': asset.secure_url,
            'web_url': asset.web_url,
            'thumb_url': asset.thumb_url,
            'album': asset.album.title if asset.album else 'Uncategorized',
            'format': asset.format,
            'width': asset.width,
            'height': asset.height,
        })
    
    return JsonResponse({'images': image_data})


def compress_image(file, max_size_bytes):
    """
    Compress an image file to fit within the specified size limit.
    Returns a new InMemoryUploadedFile with the compressed image.
    """
    from PIL import Image
    import io
    from django.core.files.uploadedfile import InMemoryUploadedFile
    
    # Open the image
    image = Image.open(file)
    
    # Convert to RGB if necessary (for JPEG compatibility)
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    # Start with high quality and reduce until we meet size requirements
    quality = 85
    min_quality = 10
    
    while quality >= min_quality:
        # Create a new file-like object
        output = io.BytesIO()
        
        # Save with current quality
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Check if size is acceptable
        if len(output.getvalue()) <= max_size_bytes:
            # Create new InMemoryUploadedFile
            compressed_file = InMemoryUploadedFile(
                output,
                None,
                file.name,
                'image/jpeg',
                len(output.getvalue()),
                None
            )
            return compressed_file
        
        # Reduce quality for next iteration
        quality -= 10
    
    # If we still can't get it small enough, try reducing dimensions
    original_size = image.size
    scale_factor = 0.8
    
    while scale_factor > 0.1:
        new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        resized_image.save(output, format='JPEG', quality=50, optimize=True)
        output.seek(0)
        
        if len(output.getvalue()) <= max_size_bytes:
            compressed_file = InMemoryUploadedFile(
                output,
                None,
                file.name,
                'image/jpeg',
                len(output.getvalue()),
                None
            )
            return compressed_file
        
        scale_factor -= 0.1
    
    # If all else fails, return the original file (it will fail at Cloudinary level)
    return file


@login_required
@require_POST
def gallery_api_upload(request):
    """API endpoint to upload new images to the gallery"""
    try:
        from .utils.cloudinary_uploads import upload_and_get_url
        from .models import MediaAlbum
        import cloudinary.uploader
        from PIL import Image
        import io
        from django.core.files.uploadedfile import InMemoryUploadedFile
        
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse({'success': False, 'error': 'No files provided'})
        
        # Get or create a default album for uploads
        default_album, created = MediaAlbum.objects.get_or_create(
            title='Uploads',
            defaults={
                'description': 'Images uploaded through the gallery',
                'cld_folder': 'uploads'
            }
        )
        
        uploaded_images = []
        
        for file in files:
            try:
                # Check file size and compress if needed
                max_size = 10 * 1024 * 1024  # 10MB limit
                if file.size > max_size:
                    # Compress the image
                    file = compress_image(file, max_size)
                
                # Upload to Cloudinary with additional transformations
                result = cloudinary.uploader.upload(
                    file,
                    folder="uploads",
                    resource_type="image",
                    overwrite=True,
                    eager=[
                        {"width": 400, "height": 300, "crop": "fill"},
                        {"width": 800, "height": 600, "crop": "fill"}
                    ]
                )
                
                # Create MediaAsset record
                asset = MediaAsset.objects.create(
                    album=default_album,
                    title=file.name.split('.')[0],  # Use filename without extension
                    public_id=result['public_id'],
                    secure_url=result['secure_url'],
                    web_url=result['secure_url'].replace('/upload/', '/upload/f_auto,q_auto/'),
                    thumb_url=result['eager'][0]['secure_url'] if result.get('eager') else result['secure_url'],
                    bytes_size=result.get('bytes', 0),
                    width=result.get('width', 0),
                    height=result.get('height', 0),
                    format=result.get('format', ''),
                )
                
                uploaded_images.append({
                    'id': asset.id,
                    'title': asset.title,
                    'secure_url': asset.secure_url,
                    'web_url': asset.web_url,
                    'thumb_url': asset.thumb_url,
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'error': f'Failed to upload {file.name}: {str(e)}'
                })
        
        return JsonResponse({
            'success': True,
            'images': uploaded_images
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# -------------------------------------------------------------------------------------- 
# User Management (Admin only)
# -------------------------------------------------------------------------------------- 

@admin_required
def dashboard_users_list(request):
    """List all users with their roles"""
    users = get_user_model().objects.select_related('profile').all().order_by('-date_joined')
    return render(request, "dashboard/users_list.html", {"users": users})


@admin_required
def dashboard_user_create(request):
    """Create a new user with role assignment"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'user')
        
        if form.is_valid():
            user = form.save()
            # Update the user's profile role
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.save()
            
            messages.success(request, f"User '{user.username}' created successfully with role '{role}'.")
            return redirect("dashboard_users_list")
    else:
        form = UserCreationForm()
    
    return render(request, "dashboard/user_form.html", {
        "form": form,
        "mode": "create"
    })


@admin_required
def dashboard_user_edit(request, pk: int):
    """Edit user role and basic info"""
    user = get_object_or_404(get_user_model(), pk=pk)
    
    if request.method == "POST":
        # Update user profile role
        if hasattr(user, 'profile'):
            new_role = request.POST.get('role', 'user')
            user.profile.role = new_role
            user.profile.save()
            
            messages.success(request, f"User '{user.username}' role updated to '{new_role}'.")
            return redirect("dashboard_users_list")
    
    return render(request, "dashboard/user_form.html", {
        "user": user,
        "mode": "edit"
    })


@admin_required
def dashboard_user_delete(request, pk: int):
    """Delete a user (admin only)"""
    user = get_object_or_404(get_user_model(), pk=pk)
    
    # Prevent deleting superusers
    if user.is_superuser:
        messages.error(request, "Cannot delete superuser accounts.")
        return redirect("dashboard_users_list")
    
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' has been deleted.")
        return redirect("dashboard_users_list")
    
    return render(request, "dashboard/confirm_delete.html", {
        "object": user, 
        "type": "User"
    })
