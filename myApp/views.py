from __future__ import annotations

import json
import logging
import time
from typing import Iterable, Mapping, Any

import requests
from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import escape
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.db.models import Q
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
    MediaAlbum,
    CaseStudy,
    InsightAuditLog,
    PageHero,
    PageMetadata,
)
from .forms import ServiceForm, InsightForm, ServiceCapabilityFormSet, ServiceEditorialImageFormSet, ServiceProjectImageFormSet, CaseStudyFormSet, ServiceProcessStepFormSet
from .utils.google_drive_utils import upload_from_google_drive_to_cloudinary, extract_file_id_from_url, bulk_upload_from_drive_folder
from .utils.cloudinary_utils import smart_compress_to_bytes, upload_to_cloudinary, TARGET_BYTES
from .utils.document_converter import convert_document_to_blocks
from .utils.ai_metadata_generator import generate_metadata_with_ai
from .spam_detection import validate_contact_submission, record_submission, get_client_ip
from .models import BlockedEmail, BlockedIP, FormSubmission

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


def verify_recaptcha(request, recaptcha_token):
    """
    Verify Google reCAPTCHA token.
    Returns (is_valid, error_message) tuple.
    """
    recaptcha_secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    recaptcha_site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
    recaptcha_verify_url = getattr(settings, 'RECAPTCHA_VERIFY_URL', 'https://www.google.com/recaptcha/api/siteverify')
    
    # If reCAPTCHA is not fully configured (missing either key), skip validation (for development)
    if not recaptcha_secret_key or not recaptcha_site_key:
        logger.debug("reCAPTCHA not fully configured (missing site or secret key) - skipping validation")
        return True, None
    
    if not recaptcha_token:
        return False, "Please complete the reCAPTCHA verification."
    
    try:
        client_ip = get_client_ip(request)
        response = requests.post(
            recaptcha_verify_url,
            data={
                'secret': recaptcha_secret_key,
                'response': recaptcha_token,
                'remoteip': client_ip,
            },
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        
        if not result.get('success', False):
            error_codes = result.get('error-codes', [])
            logger.warning(f"reCAPTCHA verification failed: {error_codes}")
            return False, "reCAPTCHA verification failed. Please try again."
        
        # Verify action name for v3 (important security check)
        action = result.get('action')
        if action and action != 'submit':
            logger.warning(f"reCAPTCHA action mismatch: expected 'submit', got '{action}'")
            return False, "reCAPTCHA verification failed. Please try again."
        
        # Check score for v3 (1.0 is very likely good, 0.0 is very likely bot)
        # v2 always returns score of 1.0, so this check works for both
        score = result.get('score', 1.0)
        if score < 0.5:  # Default threshold as recommended by Google
            logger.warning(f"reCAPTCHA score too low: {score} (threshold: 0.5)")
            return False, "reCAPTCHA verification failed. Please try again."
        
        return True, None
        
    except requests.RequestException as e:
        logger.error(f"reCAPTCHA verification error: {e}")
        # On error, fail securely (don't allow submission)
        return False, "reCAPTCHA verification error. Please try again later."


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

    # Get featured case study for each service (excluding joinery and facility management)
    case_studies_by_service = {}
    services_with_projects = []
    excluded_services = ['joinery', 'facility-management']
    
    for service in services:
        if service.slug not in excluded_services:
            # Prioritize the featured_case_study if set, otherwise get the first one
            featured_case_study = None
            if hasattr(service, 'featured_case_study') and service.featured_case_study:
                featured_case_study = service.featured_case_study
            else:
                # Fallback to first case study if no featured one is selected
                featured_case_study = (
                    CaseStudy.objects
                    .filter(service=service)
                    .order_by("sort_order", "title")
                    .first()
                )
            
            if featured_case_study:
                case_studies_by_service[service.slug] = featured_case_study
                services_with_projects.append(service)

    # Choose the first featured case study; fallback to any case study; fallback to None.
    # Exclude joinery and facility management services
    featured_cs = (
        CaseStudy.objects.select_related("service")
        .filter(is_featured=True)
        .exclude(service__slug__in=excluded_services)
        .order_by("sort_order", "title")
        .first()
        or CaseStudy.objects.select_related("service")
        .exclude(service__slug__in=excluded_services)
        .order_by("sort_order", "title")
        .first()
    )

    # Build filter data for services that have case studies (excluding joinery and facility management)
    project_filters = []
    for service in services_with_projects:
        if service.slug not in excluded_services:
            project_filters.append({
                'title': service.title,
                'slug': service.slug
            })
    
    # Get hero content for home page
    hero = PageHero.get_hero_for_page('home')

    return render(request, "index.html", {
        "services": services,
        "featured_cs": featured_cs,
        "project_filters": project_filters,
        "case_studies_by_service": case_studies_by_service,
        "hero": hero,
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
            Prefetch("case_studies",
                queryset=CaseStudy.objects.only(
                    "id","service_id","title","slug","hero_image_url","thumb_url","full_url","summary","sort_order"
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
# Legacy Views for Old URL Structure
# -----------------------------
def legacy_landscape(request):
    """Legacy view for /landscape/ - serves landscape-design-build service"""
    return service_detail(request, "landscape-design-build")

def landscape_projects(request):
    """Serve projects page filtered by landscape service at /landscape/landscaping-company-projects/"""
    return projects_index(request, service_slug='landscape-design-build')

def landscape_blog(request):
    """Serve insights/blog list filtered by landscape service at /landscape/blog/"""
    return insights_list(request, service_slug='landscape-design-build')

def legacy_landscape_catchall(request, sub_path=None):
    """
    Handle legacy /landscape/* sub-paths by serving content at the same URL (no redirects).
    This keeps the URL visible to Google while showing the appropriate content.
    
    Handles:
    - /landscape/faqs/ -> renders landscape service page (has FAQs)
    - /landscape/about/ -> renders about page
    - /landscape/blog/ -> renders insights list filtered by landscape (handled by explicit route)
    - /landscape/landscaping-company-projects/ -> renders projects filtered by landscape (handled by explicit route)
    - Any other /landscape/* -> renders landscape service page (fallback)
    """
    from django.utils.text import slugify
    
    # Extract sub_path from request if not provided as argument
    if sub_path is None:
        # Get the path from the request
        path = request.path.strip('/')
        if path.startswith('landscape/'):
            sub_path = path.replace('landscape/', '', 1).strip('/')
        else:
            sub_path = ''
    
    if sub_path:
        sub_path = sub_path.strip('/').lower()
    else:
        sub_path = ''
    
    # If empty or just whitespace, serve main landscape page
    if not sub_path:
        return service_detail(request, "landscape-design-build")
    
    # Handle specific known patterns
    if sub_path == 'faqs':
        # FAQs are on the main service page - serve it at this URL
        return service_detail(request, "landscape-design-build")
    
    if 'about' in sub_path:
        # About page - serve it at this URL
        return about(request)
    
    # Handle project URLs: /landscape/ourproject/slug/
    if sub_path.startswith('ourproject/'):
        project_slug = sub_path.replace('ourproject/', '').strip('/')
        
        # Try to find matching case study by slug
        try:
            case_study = CaseStudy.objects.filter(
                slug=project_slug
            ).first()
            
            if not case_study:
                # Try to match by partial slug
                keywords = [w for w in project_slug.split('-') if len(w) > 3]
                if keywords:
                    from django.db.models import Q
                    query = Q()
                    for keyword in keywords:
                        query |= Q(slug__icontains=keyword) | Q(title__icontains=keyword)
                    
                    case_studies = CaseStudy.objects.filter(query).filter(
                        service__slug='landscape-design-build'
                    )[:5]
                    
                    if case_studies.exists():
                        return case_study_detail(request, case_studies.first().slug)
            
            if case_study:
                return case_study_detail(request, case_study.slug)
        except Exception:
            pass
        
        # Fallback: serve projects page filtered by landscape
        try:
            return projects_index(request, service_slug='landscape-design-build')
        except:
            return projects_index(request, service_slug=None)
    
    # Default fallback: serve main landscape service page at this URL
    return service_detail(request, "landscape-design-build")

def legacy_interior(request):
    """Legacy view for /interior/ - serves interior-design-build service"""
    return service_detail(request, "interior-design-build")

def legacy_interior_catchall(request, sub_path=None):
    """
    Handle legacy /interior/* sub-paths by serving content at the same URL (no redirects).
    This keeps the URL visible to Google while showing the appropriate content.
    
    Handles:
    - /interior/faqs/ -> renders interior service page (has FAQs)
    - /interior/interior-company-about-us/ -> renders about page
    - /interior/ourproject/* -> renders case study detail or projects page if found
    - Any other /interior/* -> renders interior service page (fallback)
    """
    from django.utils.text import slugify
    
    # Extract sub_path from request if not provided as argument
    if sub_path is None:
        # Get the path from the request
        path = request.path.strip('/')
        if path.startswith('interior/'):
            sub_path = path.replace('interior/', '', 1).strip('/')
        else:
            sub_path = ''
    
    if sub_path:
        sub_path = sub_path.strip('/').lower()
    else:
        sub_path = ''
    
    # If empty or just whitespace, serve main interior page
    if not sub_path:
        return service_detail(request, "interior-design-build")
    
    # Handle specific known patterns
    if sub_path == 'faqs':
        # FAQs are on the main service page - serve it at this URL
        return service_detail(request, "interior-design-build")
    
    if 'about' in sub_path or sub_path == 'interior-company-about-us':
        # About page - serve it at this URL
        return about(request)
    
    # Handle project URLs: /interior/ourproject/slug/
    if sub_path.startswith('ourproject/'):
        project_slug = sub_path.replace('ourproject/', '').strip('/')
        
        # Try to find matching case study by slug
        # First try exact match, then try partial match on title/slug
        try:
            case_study = CaseStudy.objects.filter(
                slug=project_slug
            ).first()
            
            if not case_study:
                # Try to match by partial slug (handle variations like "kitchen-and-dinning" vs "kitchen-and-dining")
                # Extract keywords from the project slug
                keywords = [w for w in project_slug.split('-') if len(w) > 3]
                if keywords:
                    # Try to find case study with matching keywords in title or slug
                    from django.db.models import Q
                    query = Q()
                    for keyword in keywords:
                        query |= Q(slug__icontains=keyword) | Q(title__icontains=keyword)
                    
                    case_studies = CaseStudy.objects.filter(query).filter(
                        service__slug='interior-design-build'
                    )[:5]  # Limit to 5 results
                    
                    if case_studies.exists():
                        # Serve the first match at this URL
                        return case_study_detail(request, case_studies.first().slug)
            
            if case_study:
                # Serve the case study at this URL
                return case_study_detail(request, case_study.slug)
        except Exception:
            pass  # If lookup fails, fall through to projects page
        
        # Fallback: serve projects page filtered by interior at this URL
        try:
            return projects_index(request, service_slug='interior-design-build')
        except:
            return projects_index(request, service_slug=None)
    
    # Default fallback: serve main interior service page at this URL
    return service_detail(request, "interior-design-build")

def legacy_facility(request):
    """Legacy view for /facility/ - serves facility-management service"""
    return service_detail(request, "facility-management")

def legacy_aboutus(request):
    """Legacy view for /aboutus/ - serves the about page"""
    return about(request)

def legacy_blogs(request):
    """Legacy view for /blogs/ - serves the insights list page"""
    return insights_list(request)


# -----------------------------
# Public Insights List
# -----------------------------
def insights_list(request, service_slug=None):
    """
    Public-facing list of all published insights/blog posts.
    Optional filter by service via service_slug parameter.
    """
    insights = Insight.objects.filter(
        published=True,
        is_active=True
    ).select_related('service', 'author').order_by('-published_at', '-created_at')
    
    # Filter by service if provided
    current_service = None
    if service_slug:
        try:
            current_service = Service.objects.get(slug=service_slug, is_active=True)
            insights = insights.filter(service=current_service)
        except Service.DoesNotExist:
            pass  # If service not found, show all insights
    
    return render(request, "insights_list.html", {
        "insights": insights,
        "current_service": current_service
    })


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
from django.db.models import Prefetch, Q, Exists, OuterRef
from .models import Service, ServiceProjectImage, CaseStudy

def projects_index(request, service_slug=None):
    """
    Projects gallery aggregated from CaseStudy.
    - Optional filter by service via /projects/<service_slug>/
    - Pagination via ?page=#
    - Only show services & projects that actually have an image (full_url)
    - Grouped ordering: service first (sort_order, title), then projects (-is_featured, sort_order, title)
    """

    # Subquery: does this service have at least one imaged case study?
    imaged_cs_exists = CaseStudy.objects.filter(
        service_id=OuterRef("pk")
    ).exclude(
        Q(full_url__isnull=True) | Q(full_url__exact="")
    )

    # Left-rail services: only active services that actually have imaged projects
    # Exclude Facility Management from the projects page
    services = (
        Service.objects.only("id", "title", "slug", "sort_order")
        .filter(is_active=True)
        .exclude(slug="facility-management")
        .annotate(has_imaged_cs=Exists(imaged_cs_exists))
        .filter(has_imaged_cs=True)
        .order_by("sort_order", "title")
    )

    current_service = None

    # Base queryset: only imaged case studies, ordered by featured status first, then sort order
    # This ensures a diverse mix of projects from all services on the first page
    # Exclude Facility Management projects
    case_studies_qs = (
        CaseStudy.objects.select_related("service")
        .only(
            "id", "service_id", "title", "thumb_url", "full_url",
            "summary", "is_featured", "sort_order", "slug"
        )
        .exclude(Q(full_url__isnull=True) | Q(full_url__exact=""))
        .exclude(service__slug="facility-management")
        .order_by(
            "-is_featured",           # featured projects first
            "sort_order",             # then by sort order
            "title",                  # then alphabetically
            "id"                      # tie-breaker
        )
    )

    if service_slug:
        # Only allow services that *actually* have imaged case studies
        current_service = get_object_or_404(services, slug=service_slug)
        case_studies_qs = case_studies_qs.filter(service=current_service)

    # paginate (30 per page for better showcase)
    paginator = Paginator(case_studies_qs, 30)
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
    
    # Get hero content for projects page
    hero = PageHero.get_hero_for_page('projects')

    ctx = {
        "services": services,               # left rail shows only services with imaged projects
        "current_service": current_service, # may be None
        "page_obj": page_obj,               # items are image-only & grouped by service
        "meta_title": meta_title,
        "meta_desc": meta_desc,
        "hero": hero,                       # Add hero content
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
    
    # Get hero content for about page
    hero = PageHero.get_hero_for_page('about')
    
    # Fallback hero image URL for about page
    hero_image_url = hero.hero_image_url if hero and hero.hero_image_url else 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=2000&auto=format&fit=crop'

    ctx = {
        "hero": hero,
        "hero_image_url": hero_image_url,
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
    ("Marble", "Marble"),
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
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g., Dubai - Jumeirah Park (optional)"}),
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


class TeamMemberForm(forms.ModelForm):
    """Form for creating/editing team members"""
    class Meta:
        model = TeamMember
        fields = ['name', 'role', 'bio', 'photo_url', 'email', 'linkedin_url', 'is_active', 'is_featured', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'role': forms.TextInput(attrs={'placeholder': 'Job title or role'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief bio or description'}),
            'photo_url': forms.URLInput(attrs={'placeholder': 'https://res.cloudinary.com/...'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/...'}),
            'sort_order': forms.NumberInput(attrs={'min': 0, 'max': 999}),
        }
        labels = {
            'photo_url': 'Photo URL',
            'linkedin_url': 'LinkedIn URL',
            'is_active': 'Active',
            'is_featured': 'Featured (shows on About page)',
            'sort_order': 'Sort Order (0 = first)',
        }
        help_texts = {
            'photo_url': 'Use Cloudinary URLs for best results. Images will be automatically optimized.',
            'is_featured': 'Featured team members appear on the About page carousel.',
            'sort_order': 'Lower numbers appear first. Leave as 0 for default ordering.',
        }


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
        recaptcha_site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
        # Debug: Check if key is loaded
        if not recaptcha_site_key:
            logger.warning("RECAPTCHA_SITE_KEY is empty. Check environment variables or .env file.")
            # Try direct import to debug
            import os
            env_key = os.getenv('RECAPTCHA_SITE_KEY', '')
            if env_key:
                logger.warning(f"RECAPTCHA_SITE_KEY found in os.getenv but not in settings. Value: {env_key[:10]}...")
            else:
                logger.warning("RECAPTCHA_SITE_KEY not found in environment variables.")
        else:
            logger.debug(f"reCAPTCHA site key loaded: {recaptcha_site_key[:10]}...")
        return render(request, "contact.html", {
            "form": form,
            "recaptcha_site_key": recaptcha_site_key or '',  # Ensure it's always a string
        })

    # POST
    recaptcha_site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
    form = ContactForm(request.POST)
    if not form.is_valid():
        if _is_ajax(request):
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        messages.error(request, "Please correct the errors and try again.")
        return render(request, "contact.html", {
            "form": form,
            "recaptcha_site_key": recaptcha_site_key,
        })

    data = form.cleaned_data
    
    # reCAPTCHA verification - Check before processing
    recaptcha_token = request.POST.get('g-recaptcha-response', '')
    recaptcha_valid, recaptcha_error = verify_recaptcha(request, recaptcha_token)
    
    if not recaptcha_valid:
        logger.warning(f"reCAPTCHA failed for submission: {data.get('email', 'unknown')}")
        if _is_ajax(request):
            return JsonResponse({"ok": False, "errors": {"__all__": [recaptcha_error]}}, status=400)
        messages.error(request, recaptcha_error)
        return render(request, "contact.html", {
            "form": form,
            "recaptcha_site_key": recaptcha_site_key,
        })
    
    # SPAM DETECTION - Check before processing
    is_valid, error_message, should_block = validate_contact_submission(request, data)
    
    if not is_valid:
        logger.warning(f"Spam/rejected submission: {data.get('email')} - {error_message}")
        
        # If spam score is very high, optionally block the email/IP automatically
        if should_block:
            email = data.get('email', '').strip().lower()
            ip_address = get_client_ip(request)
            
            # Auto-block if spam score is very high (you can disable this if preferred)
            if email and getattr(settings, 'AUTO_BLOCK_SPAM', False):
                from .models import BlockedEmail, BlockedIP
                BlockedEmail.objects.get_or_create(
                    email=email,
                    defaults={'reason': 'Auto-blocked due to high spam score', 'is_active': True}
                )
            if ip_address and getattr(settings, 'AUTO_BLOCK_SPAM', False):
                from .models import BlockedIP
                BlockedIP.objects.get_or_create(
                    ip_address=ip_address,
                    defaults={'reason': 'Auto-blocked due to high spam score', 'is_active': True}
                )
        
        if _is_ajax(request):
            return JsonResponse({"ok": False, "errors": {"__all__": [error_message]}}, status=400)
        messages.error(request, error_message)
        recaptcha_site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
        return render(request, "contact.html", {
            "form": form,
            "recaptcha_site_key": recaptcha_site_key,
        })
    
    # Record submission for rate limiting (before sending email)
    ip_address = get_client_ip(request)
    record_submission(
        email=data['email'],
        ip_address=ip_address,
        name=data['name'],
        service=data.get('service', ''),
        message=data.get('message', '')
    )
    
    service = data.get("service") or "General"
    location = data.get("location", "")
    subject = f"[Enquiry] {service} — {data['name']}"

    # Build safe plain text (readable in any client)
    text_lines = [
        f"Name: {data['name']}",
        f"Email: {data['email']}",
        f"Phone: {data.get('phone', '')}",
        f"Service: {service}",
    ]
    if location:
        text_lines.append(f"Location: {location}")
    text_lines.extend([
        "",
        "Message:",
        data["message"],
        "",
    ])
    text = "\n".join(text_lines)

    # SAFELY escape + convert newlines -> <br> for HTML version
    safe_message_html = escape(data["message"]).replace("\n", "<br>")

    html_parts = [
        "<div style='font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;'>",
        "<h2 style='margin:0 0 12px 0;'>New enquiry</h2>",
        "<p><strong>Name:</strong> " + escape(data["name"]) + "</p>",
        "<p><strong>Email:</strong> " + escape(data["email"]) + "</p>",
        "<p><strong>Phone:</strong> " + escape(data.get("phone", "")) + "</p>",
        "<p><strong>Service:</strong> " + escape(service) + "</p>",
    ]
    if location:
        html_parts.append("<p><strong>Location:</strong> " + escape(location) + "</p>")
    html_parts.extend([
        "<hr style='border:none;border-top:1px solid #e5e7eb;margin:12px 0'>",
        "<p><strong>Message:</strong><br>" + safe_message_html + "</p>",
        "</div>"
    ])
    html = "".join(html_parts)

    to_addr = getattr(settings, "CONTACT_TO_EMAIL", getattr(settings, "DEFAULT_FROM_EMAIL", None))
    if not to_addr:
        # fall back hard to avoid silent drop
        to_addr = data["email"]

    # Send notification email to Hammer team
    ok, detail = send_email_resend(
        subject=subject,
        to=[to_addr],
        text=text,
        html=html,
        reply_to=data["email"],
        tags={"env": getattr(settings, "ENVIRONMENT", "prod"), "type": "contact"},
    )
    
    if ok:
        logger.info(f"✅ Contact notification sent to {to_addr} from {data['email']}")
    else:
        logger.error(f"❌ Contact notification failed: {detail}")

    # Send auto-response confirmation to user
    if ok:
        # Add delay to avoid Resend rate limit (2 requests/second)
        time.sleep(0.6)
        
        auto_response_subject = f"Thank you for your enquiry - {service}"
        
        # Build user-facing text
        user_text_parts = [
            f"Dear {data['name']},",
            "",
            f"Thank you for submitting your booking request for {service}",
        ]
        if location:
            user_text_parts[2] += f" in {location}"
        user_text_parts[2] += "."
        
        user_text_parts.extend([
            "",
            "Your request details:",
            f"- Project Type: {service}",
        ])
        if location:
            user_text_parts.append(f"- Location: {location}")
        if data.get("message"):
            user_text_parts.extend([
                f"- Message: {data['message'][:100]}{'...' if len(data['message']) > 100 else ''}",
            ])
        
        user_text_parts.extend([
            "",
            "We have received your request and will review it shortly. Our team will contact you within 24-48 hours to discuss your project requirements and provide you with a detailed quote.",
            "",
            "If you have any urgent questions, please don't hesitate to contact us directly.",
            "",
            "Best regards,",
            "The Hammer Group Team",
        ])
        user_text = "\n".join(user_text_parts)
        
        # Build HTML version
        user_html_parts = [
            "<div style='font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:600px;margin:0 auto;'>",
            f"<p>Dear {escape(data['name'])},</p>",
            f"<p>Thank you for submitting your booking request for <strong>{escape(service)}</strong>",
        ]
        if location:
            user_html_parts[-1] += f" in <strong>{escape(location)}</strong>"
        user_html_parts[-1] += ".</p>"
        
        user_html_parts.extend([
            "<div style='background-color:#f9fafb;border-left:4px solid #18AFAB;padding:16px;margin:20px 0;'>",
            "<h3 style='margin:0 0 12px 0;color:#18AFAB;font-size:16px;'>Your request details:</h3>",
            f"<p style='margin:4px 0;'><strong>Project Type:</strong> {escape(service)}</p>",
        ])
        if location:
            user_html_parts.append(f"<p style='margin:4px 0;'><strong>Location:</strong> {escape(location)}</p>")
        if data.get("message"):
            user_html_parts.append(f"<p style='margin:4px 0;'><strong>Message:</strong> {escape(data['message'][:150])}{'...' if len(data['message']) > 150 else ''}</p>")
        
        user_html_parts.extend([
            "</div>",
            "<p>We have received your request and will review it shortly. <strong>Our team will contact you within 24-48 hours</strong> to discuss your project requirements and provide you with a detailed quote.</p>",
            "<p>If you have any urgent questions, please don't hesitate to contact us directly.</p>",
            "<p style='margin-top:30px;'>Best regards,<br><strong style='color:#18AFAB;'>The Hammer Group Team</strong></p>",
            "</div>",
        ])
        user_html = "".join(user_html_parts)
        
        # Send auto-response (don't fail if this doesn't work)
        try:
            auto_ok, auto_detail = send_email_resend(
                subject=auto_response_subject,
                to=[data["email"]],
                text=user_text,
                html=user_html,
                reply_to=to_addr,
                tags={"env": getattr(settings, "ENVIRONMENT", "prod"), "type": "auto_response"},
            )
            if auto_ok:
                logger.info(f"✅ Auto-response sent successfully to {data['email']}")
            else:
                logger.warning(f"⚠️ Auto-response failed to {data['email']}: {auto_detail}")
        except Exception as e:
            logger.error(f"❌ Failed to send auto-response to {data['email']}: {e}")

    if _is_ajax(request):
        status = 200 if ok else 502
        if ok:
            # Return success with redirect URL for AJAX
            return JsonResponse({
                "ok": ok, 
                "detail": detail,
                "redirect": reverse('thank_you')
            }, status=status)
        return JsonResponse({"ok": ok, "detail": detail}, status=status)

    if ok:
        messages.success(request, "Thanks — your message is on its way. We'll get back to you shortly.")
        # Redirect to beautiful thank you page
        return redirect('thank_you')
    else:
        messages.error(request, "Sorry, we couldn't send your message. Please try again in a moment.")
        recaptcha_site_key = getattr(settings, 'RECAPTCHA_SITE_KEY', '')
        return render(request, "contact.html", {
            "form": form,
            "recaptcha_site_key": recaptcha_site_key or '',
        })


def thank_you(request: HttpRequest) -> HttpResponse:
    """
    Beautiful thank you page displayed after successful form submission.
    """
    return render(request, "thank_you.html", {})


# myApp/views.py
from django.shortcuts import get_object_or_404, render
from .models import TeamMember

def team_detail(request, slug):
    person = get_object_or_404(TeamMember, slug=slug, is_active=True)
    return render(request, "team/detail.html", {"person": person})


# --------------------------------------------------------------------------------------
# Case Study Detail
# --------------------------------------------------------------------------------------
from .models import CaseStudy

def case_study_detail(request, slug):
    """
    Case study detail page showing project information and related details.
    Images are now stored directly on the CaseStudy model (hero_image_url, thumb_url, full_url).
    """
    case_study = get_object_or_404(
        CaseStudy.objects.select_related('service'),
        slug=slug
    )
    
    # Build gallery from gallery_urls field (new approach) or legacy_images (backwards compatibility)
    gallery_images = []
    
    # First, try the new gallery_urls field
    if case_study.gallery_urls:
        class GalleryImage:
            def __init__(self, thumb, full, caption=''):
                self.thumb_url = thumb
                self.full_url = full
                self.caption = caption
        
        for img_data in case_study.gallery_urls:
            if isinstance(img_data, dict) and 'full' in img_data and 'thumb' in img_data:
                gallery_images.append(GalleryImage(
                    img_data.get('thumb', ''),
                    img_data.get('full', ''),
                    case_study.title
                ))
    
    # Fallback to legacy images if no gallery_urls
    if not gallery_images:
        gallery_images = list(case_study.legacy_images.all().order_by('sort_order', 'id'))
    
    # Final fallback: use the main case study images
    if not gallery_images and case_study.full_url:
        class GalleryImage:
            def __init__(self, thumb, full, caption=''):
                self.thumb_url = thumb
                self.full_url = full
                self.caption = caption
        
        gallery_images = [GalleryImage(
            case_study.thumb_url or case_study.hero_image_url,
            case_study.full_url or case_study.hero_image_url,
            case_study.title
        )]
    
    # Get related case studies from the same service
    related_case_studies = (
        CaseStudy.objects
        .filter(service=case_study.service)
        .exclude(id=case_study.id)
        .order_by('-is_featured', 'sort_order')[:3]
    )
    
    return render(request, "case_studies/detail.html", {
        "case_study": case_study,
        "gallery_images": gallery_images,
        "related_case_studies": related_case_studies,
    })


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
        case_study_formset = CaseStudyFormSet(request.POST, prefix='case_studies')
        process_formset = ServiceProcessStepFormSet(request.POST, prefix='process_steps')
        
        if form.is_valid() and capability_formset.is_valid() and image_formset.is_valid() and case_study_formset.is_valid() and process_formset.is_valid():
            service = form.save()
            capability_formset.instance = service
            capability_formset.save()
            image_formset.instance = service
            image_formset.save()
            
            # Save case studies
            case_studies = case_study_formset.save(commit=False)
            for cs in case_studies:
                cs.service = service
                cs.save()
            case_study_formset.save_m2m()
            
            # Save process steps
            process_formset.instance = service
            process_formset.save()
            
            messages.success(request, "Service created successfully!")
            return redirect(service.get_absolute_url())
    else:
        form = ServiceForm()
        capability_formset = ServiceCapabilityFormSet(prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(prefix='images')
        case_study_formset = CaseStudyFormSet(prefix='case_studies')
        process_formset = ServiceProcessStepFormSet(prefix='process_steps')
    
    return render(request, "dashboard/service_form.html", {
        "form": form, 
        "capability_formset": capability_formset,
        "image_formset": image_formset,
        "case_study_formset": case_study_formset,
        "process_formset": process_formset,
        "mode": "create"
    })


@login_required
def dashboard_service_edit(request, pk: int):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        capability_formset = ServiceCapabilityFormSet(request.POST, instance=service, prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(request.POST, instance=service, prefix='images')
        case_study_formset = CaseStudyFormSet(request.POST, instance=service, prefix='case_studies')
        process_formset = ServiceProcessStepFormSet(request.POST, instance=service, prefix='process_steps')
        
        # Validate all forms
        form_valid = form.is_valid()
        capability_valid = capability_formset.is_valid()
        image_valid = image_formset.is_valid()
        case_study_valid = case_study_formset.is_valid()
        process_valid = process_formset.is_valid()
        
        if form_valid and capability_valid and image_valid and case_study_valid and process_valid:
            service = form.save()
            capability_formset.save()
            image_formset.save()
            
            # Save case studies with proper error handling
            case_studies = case_study_formset.save(commit=False)
            for cs in case_studies:
                if not cs.pk:
                    cs.service = service
                try:
                    # Debug gallery_urls before saving
                    print(f"DEBUG: Saving case study {cs.id or 'new'} with gallery_urls: {cs.gallery_urls}")
                    cs.save()
                except IntegrityError as e:
                    print(f"ERROR: Integrity error saving case study: {e}")
                    # If there's a duplicate key error, try to get the existing object
                    if 'duplicate key' in str(e).lower():
                        # Try to find existing case study with same slug or title
                        try:
                            existing_cs = CaseStudy.objects.get(
                                service=service,
                                slug=cs.slug
                            )
                            # Update the existing case study
                            existing_cs.title = cs.title
                            existing_cs.gallery_urls = cs.gallery_urls
                            existing_cs.summary = cs.summary
                            existing_cs.description = cs.description
                            existing_cs.completion_date = cs.completion_date
                            existing_cs.scope = cs.scope
                            existing_cs.timeline = cs.timeline
                            existing_cs.tags = cs.tags
                            existing_cs.save()
                            print(f"Updated existing case study: {existing_cs.id}")
                        except CaseStudy.DoesNotExist:
                            # If we can't find existing, create new with different slug
                            cs.slug = f"{cs.slug}-{cs.pk or 'new'}"
                            cs.save()
                            print(f"Created new case study with modified slug: {cs.slug}")
                    else:
                        raise e
            
            # Delete marked case studies
            deleted_count = 0
            for obj in case_study_formset.deleted_objects:
                obj.delete()
                deleted_count += 1
            
            if deleted_count > 0:
                messages.info(request, f"{deleted_count} project(s) deleted.")
            
            case_study_formset.save_m2m()
            
            # Save process steps
            process_formset.save()
            
            messages.success(request, "Service updated successfully!")
            return redirect("dashboard_services_list")
        else:
            # Add error messages for debugging
            if not form_valid:
                messages.error(request, f"Service form errors: {form.errors}")
            if not capability_valid:
                messages.error(request, f"Capability formset errors: {capability_formset.errors}")
            if not image_valid:
                messages.error(request, f"Image formset errors: {image_formset.errors}")
            if not case_study_valid:
                messages.error(request, f"Case study formset errors: {case_study_formset.errors}")
            if not process_valid:
                messages.error(request, f"Process steps formset errors: {process_formset.errors}")
    else:
        form = ServiceForm(instance=service)
        capability_formset = ServiceCapabilityFormSet(instance=service, prefix='capabilities')
        image_formset = ServiceEditorialImageFormSet(instance=service, prefix='images')
        case_study_formset = CaseStudyFormSet(instance=service, prefix='case_studies')
        process_formset = ServiceProcessStepFormSet(instance=service, prefix='process_steps')
    
    return render(request, "dashboard/service_form.html", {
        "form": form, 
        "capability_formset": capability_formset,
        "image_formset": image_formset,
        "case_study_formset": case_study_formset,
        "process_formset": process_formset,
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
    
    return render(request, "dashboard/insight_form_new.html", {
        "form": form, 
        "mode": "create",
        "insight": None,  # No insight object for create mode
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
            
            # Slug is auto-generated by form's clean_slug method, but ensure it exists as fallback
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
    
    return render(request, "dashboard/insight_form_new.html", {
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


@require_POST
@blog_author_required
def dashboard_insight_upload_document(request):
    """
    Upload a Word document or PDF and convert it to Editor.js blocks format.
    Returns JSON with the blocks data that can be loaded into the editor.
    """
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file provided"}, status=400)
    
    filename = file.name.lower()
    if not (filename.endswith('.docx') or filename.endswith('.pdf')):
        return JsonResponse({"error": "Unsupported file type. Please upload a .docx or .pdf file."}, status=400)
    
    try:
        # Convert document to Editor.js blocks
        blocks_data = convert_document_to_blocks(file)
        
        # Extract title from first heading or first paragraph
        title = ""
        if blocks_data.get("blocks"):
            first_block = blocks_data["blocks"][0]
            if first_block.get("type") == "header":
                title = first_block.get("data", {}).get("text", "")
            elif first_block.get("type") == "paragraph":
                # Use first paragraph as title (truncated)
                title = first_block.get("data", {}).get("text", "")[:100]
        
        return JsonResponse({
            "success": True,
            "blocks": blocks_data,
            "title": title,
            "message": f"Successfully converted {filename}"
        })
    except ImportError as e:
        return JsonResponse({"error": str(e)}, status=500)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logging.error(f"Error converting document: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"Error processing document: {str(e)}"}, status=500)


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
                # Read file content
                file.seek(0)
                file_bytes = file.read()
                
                # Auto-compress if file is too large (>10MB)
                if len(file_bytes) > TARGET_BYTES:
                    file.seek(0)
                    file_bytes = smart_compress_to_bytes(file)
                
                # Generate clean public_id from filename
                from django.utils.text import slugify
                base_name = file.name.rsplit('.', 1)[0] if '.' in file.name else file.name
                public_id = slugify(base_name)[:120]
                
                # Upload to Cloudinary using utility function
                result, web_url, thumb_url = upload_to_cloudinary(
                    file_bytes=file_bytes,
                    folder="uploads",
                    public_id=public_id,
                    tags=None
                )
                
                # Create MediaAsset record
                asset = MediaAsset.objects.create(
                    album=default_album,
                    title=file.name.split('.')[0],  # Use filename without extension
                    public_id=result.get('public_id', ''),
                    secure_url=result.get('secure_url', ''),
                    web_url=web_url,
                    thumb_url=thumb_url,
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


@login_required
@require_POST
def gallery_api_delete(request):
    """API endpoint to delete gallery images"""
    try:
        from .models import MediaAsset
        import json
        
        data = json.loads(request.body)
        image_id = data.get('image_id')
        
        if not image_id:
            return JsonResponse({'success': False, 'error': 'No image ID provided'})
        
        try:
            asset = MediaAsset.objects.get(id=image_id, is_active=True)
            # Soft delete by setting is_active to False
            asset.is_active = False
            asset.save()
            
            return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
            
        except MediaAsset.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def google_drive_upload(request):
    """
    Upload an image from Google Drive to Cloudinary with automatic compression.
    
    Expects JSON body with:
    - drive_url: Google Drive shareable link or file ID
    - album_id: (optional) MediaAlbum ID to assign the uploaded image to
    - tags: (optional) Comma-separated tags
    - auto_compress: (optional, default: true) Whether to compress large files
    """
    try:
        import json
        data = json.loads(request.body)
        
        drive_url = data.get('drive_url')
        if not drive_url:
            return JsonResponse({
                'success': False,
                'error': 'drive_url is required'
            }, status=400)
        
        # Get album or use default
        album_id = data.get('album_id')
        if album_id:
            album = get_object_or_404(MediaAlbum, pk=album_id)
        else:
            # Get or create default album
            album, created = MediaAlbum.objects.get_or_create(
                title='Google Drive Uploads',
                defaults={
                    'description': 'Images uploaded from Google Drive',
                    'cld_folder': 'google_drive_uploads'
                }
            )
        
        # Parse tags
        tags_str = data.get('tags', '')
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        if album.default_tags:
            tags += [t.strip() for t in album.default_tags.split(',') if t.strip()]
        
        # Auto compress setting
        auto_compress = data.get('auto_compress', True)
        
        # Upload from Google Drive to Cloudinary
        cloudinary_folder = album.cld_folder or 'uploads'
        result, web_url, thumb_url, drive_metadata = upload_from_google_drive_to_cloudinary(
            drive_file_id_or_url=drive_url,
            cloudinary_folder=cloudinary_folder,
            tags=tags,
            auto_compress=auto_compress
        )
        
        # Create MediaAsset record
        from django.utils.text import slugify
        title = drive_metadata.get('name', 'Google Drive Upload')
        if '.' in title:
            title = title.rsplit('.', 1)[0]
        
        asset = MediaAsset.objects.create(
            album=album,
            title=title,
            public_id=result.get('public_id', ''),
            secure_url=result.get('secure_url', ''),
            web_url=web_url,
            thumb_url=thumb_url,
            bytes_size=result.get('bytes', 0),
            width=result.get('width', 0),
            height=result.get('height', 0),
            format=result.get('format', ''),
            tags_csv=', '.join(tags) if tags else '',
        )
        
        return JsonResponse({
            'success': True,
            'image': {
                'id': asset.id,
                'title': asset.title,
                'secure_url': asset.secure_url,
                'web_url': asset.web_url,
                'thumb_url': asset.thumb_url,
                'public_id': asset.public_id,
            },
            'drive_metadata': {
                'original_name': drive_metadata.get('name'),
                'mime_type': drive_metadata.get('mimeType'),
                'size': drive_metadata.get('size'),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def google_drive_bulk_upload(request):
    """
    Upload multiple images from a Google Drive folder to Cloudinary.
    
    Expects JSON body with:
    - folder_url: Google Drive folder shareable link or folder ID
    - album_id: (optional) MediaAlbum ID to assign uploaded images to
    - tags: (optional) Comma-separated tags
    - auto_compress: (optional, default: true) Whether to compress large files
    """
    try:
        import json
        data = json.loads(request.body)
        
        folder_url = data.get('folder_url')
        if not folder_url:
            return JsonResponse({
                'success': False,
                'error': 'folder_url is required'
            }, status=400)
        
        # Extract folder ID
        folder_id = extract_file_id_from_url(folder_url)
        if not folder_id:
            return JsonResponse({
                'success': False,
                'error': 'Invalid Google Drive folder URL'
            }, status=400)
        
        # Get album or use default
        album_id = data.get('album_id')
        if album_id:
            album = get_object_or_404(MediaAlbum, pk=album_id)
        else:
            album, created = MediaAlbum.objects.get_or_create(
                title='Google Drive Uploads',
                defaults={
                    'description': 'Images uploaded from Google Drive',
                    'cld_folder': 'google_drive_uploads'
                }
            )
        
        # Parse tags
        tags_str = data.get('tags', '')
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        if album.default_tags:
            tags += [t.strip() for t in album.default_tags.split(',') if t.strip()]
        
        # Auto compress setting
        auto_compress = data.get('auto_compress', True)
        
        # Bulk upload from Google Drive folder
        cloudinary_folder = album.cld_folder or 'uploads'
        results = bulk_upload_from_drive_folder(
            folder_id=folder_id,
            cloudinary_folder=cloudinary_folder,
            tags=tags,
            auto_compress=auto_compress
        )
        
        # Create MediaAsset records for successful uploads
        created_assets = []
        failed_uploads = []
        
        for result in results:
            if result['success']:
                try:
                    from django.utils.text import slugify
                    title = result['drive_name']
                    if '.' in title:
                        title = title.rsplit('.', 1)[0]
                    
                    # Find the Cloudinary result by public_id
                    # We need to fetch it to get all metadata
                    import cloudinary.api
                    cloud_result = cloudinary.api.resource(result['public_id'])
                    
                    asset = MediaAsset.objects.create(
                        album=album,
                        title=title,
                        public_id=result['public_id'],
                        secure_url=cloud_result.get('secure_url', ''),
                        web_url=result['cloudinary_url'],
                        thumb_url=cloud_result.get('secure_url', '').replace('/upload/', '/upload/c_fill,w_480,h_320/'),
                        bytes_size=cloud_result.get('bytes', 0),
                        width=cloud_result.get('width', 0),
                        height=cloud_result.get('height', 0),
                        format=cloud_result.get('format', ''),
                        tags_csv=', '.join(tags) if tags else '',
                    )
                    
                    created_assets.append({
                        'id': asset.id,
                        'title': asset.title,
                        'web_url': asset.web_url,
                        'drive_name': result['drive_name']
                    })
                except Exception as e:
                    failed_uploads.append({
                        'drive_name': result['drive_name'],
                        'error': f'Failed to create MediaAsset: {str(e)}'
                    })
            else:
                failed_uploads.append({
                    'drive_name': result['drive_name'],
                    'error': result['error']
                })
        
        return JsonResponse({
            'success': True,
            'uploaded': len(created_assets),
            'failed': len(failed_uploads),
            'images': created_assets,
            'errors': failed_uploads
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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


# Team Management Views
@login_required
def dashboard_team_list(request):
    """List all team members"""
    team_members = TeamMember.objects.all().order_by('sort_order', 'name')
    return render(request, "dashboard/team_list.html", {
        "team_members": team_members
    })


@login_required
def dashboard_team_create(request):
    """Create a new team member"""
    if request.method == "POST":
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            team_member = form.save()
            messages.success(request, f"Team member '{team_member.name}' has been created.")
            return redirect("dashboard_team_list")
    else:
        form = TeamMemberForm()
    
    return render(request, "dashboard/team_form.html", {
        "form": form,
        "title": "Add Team Member"
    })


@login_required
def dashboard_team_edit(request, pk: int):
    """Edit a team member"""
    team_member = get_object_or_404(TeamMember, pk=pk)
    
    if request.method == "POST":
        form = TeamMemberForm(request.POST, instance=team_member)
        if form.is_valid():
            team_member = form.save()
            messages.success(request, f"Team member '{team_member.name}' has been updated.")
            return redirect("dashboard_team_list")
    else:
        form = TeamMemberForm(instance=team_member)
    
    return render(request, "dashboard/team_form.html", {
        "form": form,
        "title": f"Edit {team_member.name}",
        "team_member": team_member
    })


@login_required
@require_POST
def dashboard_team_delete(request, pk: int):
    """Delete a team member"""
    team_member = get_object_or_404(TeamMember, pk=pk)
    name = team_member.name
    team_member.delete()
    messages.success(request, f"Team member '{name}' has been deleted.")
    return redirect("dashboard_team_list")


# -------------------------------------------------------------------------------------- 
# Hero Management (Superuser only)
# -------------------------------------------------------------------------------------- 

@admin_required
def dashboard_heroes_list(request):
    """List all page heroes"""
    heroes = PageHero.objects.all().order_by('page')
    return render(request, "dashboard/heroes_list.html", {"heroes": heroes})


@admin_required
def dashboard_hero_create(request):
    """Create a new page hero"""
    if request.method == "POST":
        # Parse form data
        page = request.POST.get('page')
        title = request.POST.get('title')
        eyebrow = request.POST.get('eyebrow', '')
        headline = request.POST.get('headline')
        subtext = request.POST.get('subtext', '')
        hero_image_url = request.POST.get('hero_image_url', '')
        image_position = request.POST.get('image_position', '50% 50%')
        is_active = request.POST.get('is_active') == 'on'
        
        # Parse buttons (JSON)
        buttons_json = request.POST.get('buttons', '[]')
        try:
            buttons = json.loads(buttons_json)
        except json.JSONDecodeError:
            buttons = []
        
        # Parse pills (JSON or comma-separated)
        pills_json = request.POST.get('pills', '[]')
        try:
            pills = json.loads(pills_json)
        except json.JSONDecodeError:
            # Try comma-separated fallback
            pills = [p.strip() for p in pills_json.split(',') if p.strip()]
        
        # Create hero
        try:
            hero = PageHero.objects.create(
                page=page,
                title=title,
                eyebrow=eyebrow,
                headline=headline,
                subtext=subtext,
                hero_image_url=hero_image_url,
                image_position=image_position,
                buttons=buttons,
                pills=pills,
                is_active=is_active
            )
            messages.success(request, f"Hero for '{hero.get_page_display()}' page created successfully!")
            return redirect("dashboard_heroes_list")
        except Exception as e:
            messages.error(request, f"Error creating hero: {str(e)}")
    
    # Available pages that don't have a hero yet
    existing_pages = PageHero.objects.values_list('page', flat=True)
    available_pages = [
        (code, label) for code, label in PageHero.PAGE_CHOICES 
        if code not in existing_pages
    ]
    
    return render(request, "dashboard/hero_form.html", {
        "mode": "create",
        "available_pages": available_pages,
        "page_choices": PageHero.PAGE_CHOICES
    })


@admin_required
def dashboard_hero_edit(request, pk: int):
    """Edit a page hero"""
    hero = get_object_or_404(PageHero, pk=pk)
    
    if request.method == "POST":
        # Parse form data
        hero.title = request.POST.get('title', hero.title)
        hero.eyebrow = request.POST.get('eyebrow', '')
        hero.headline = request.POST.get('headline')
        hero.subtext = request.POST.get('subtext', '')
        hero.hero_image_url = request.POST.get('hero_image_url', '')
        hero.image_position = request.POST.get('image_position', '50% 50%')
        hero.is_active = request.POST.get('is_active') == 'on'
        
        # Parse buttons (JSON)
        buttons_json = request.POST.get('buttons', '[]')
        try:
            hero.buttons = json.loads(buttons_json)
        except json.JSONDecodeError:
            hero.buttons = []
        
        # Parse pills (JSON or comma-separated)
        pills_json = request.POST.get('pills', '[]')
        try:
            hero.pills = json.loads(pills_json)
        except json.JSONDecodeError:
            # Try comma-separated fallback
            hero.pills = [p.strip() for p in pills_json.split(',') if p.strip()]
        
        try:
            hero.save()
            messages.success(request, f"Hero for '{hero.get_page_display()}' page updated successfully!")
            return redirect("dashboard_heroes_list")
        except Exception as e:
            messages.error(request, f"Error updating hero: {str(e)}")
    
    return render(request, "dashboard/hero_form.html", {
        "mode": "edit",
        "hero": hero,
        "page_choices": PageHero.PAGE_CHOICES,
        "buttons_json": json.dumps(hero.buttons),
        "pills_json": json.dumps(hero.pills)
    })


@admin_required
@require_POST
def dashboard_hero_delete(request, pk: int):
    """Delete a page hero"""
    hero = get_object_or_404(PageHero, pk=pk)
    page_name = hero.get_page_display()
    hero.delete()
    messages.success(request, f"Hero for '{page_name}' page has been deleted.")
    return redirect("dashboard_heroes_list")


# ============================================
# Metadata Management Dashboard Views
# ============================================

@admin_required
def dashboard_metadata_list(request):
    """List all page metadata entries"""
    metadata_list = PageMetadata.objects.order_by("url_path")
    
    # Calculate stats
    total_pages = metadata_list.count()
    with_metadata = sum(1 for m in metadata_list if m.meta_title)
    missing_metadata = total_pages - with_metadata
    active_count = sum(1 for m in metadata_list if m.is_active)
    
    context = {
        "metadata_list": metadata_list,
        "total_pages": total_pages,
        "with_metadata": with_metadata,
        "missing_metadata": missing_metadata,
        "active_count": active_count,
    }
    return render(request, "dashboard/metadata_list.html", context)


@admin_required
def dashboard_metadata_create(request):
    """Create new page metadata"""
    if request.method == "POST":
        try:
            metadata = PageMetadata.objects.create(
                url_path=request.POST.get('url_path', '').strip(),
                page_name=request.POST.get('page_name', '').strip(),
                meta_title=request.POST.get('meta_title', '').strip(),
                meta_description=request.POST.get('meta_description', '').strip(),
                meta_keywords=request.POST.get('meta_keywords', '').strip(),
                og_title=request.POST.get('og_title', '').strip(),
                og_description=request.POST.get('og_description', '').strip(),
                og_image=request.POST.get('og_image', '').strip(),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, f"Metadata for '{metadata.page_name}' created successfully!")
            return redirect("dashboard_metadata_list")
        except Exception as e:
            messages.error(request, f"Error creating metadata: {str(e)}")
    
    return render(request, "dashboard/metadata_form.html", {"mode": "create"})


@admin_required
def dashboard_metadata_edit(request, pk: int):
    """Edit page metadata"""
    metadata = get_object_or_404(PageMetadata, pk=pk)
    
    if request.method == "POST":
        try:
            metadata.url_path = request.POST.get('url_path', '').strip()
            metadata.page_name = request.POST.get('page_name', '').strip()
            metadata.meta_title = request.POST.get('meta_title', '').strip()
            metadata.meta_description = request.POST.get('meta_description', '').strip()
            metadata.meta_keywords = request.POST.get('meta_keywords', '').strip()
            metadata.og_title = request.POST.get('og_title', '').strip()
            metadata.og_description = request.POST.get('og_description', '').strip()
            metadata.og_image = request.POST.get('og_image', '').strip()
            metadata.is_active = request.POST.get('is_active') == 'on'
            metadata.save()
            messages.success(request, f"Metadata for '{metadata.page_name}' updated successfully!")
            return redirect("dashboard_metadata_list")
        except Exception as e:
            messages.error(request, f"Error updating metadata: {str(e)}")
    
    return render(request, "dashboard/metadata_form.html", {"mode": "edit", "metadata": metadata})


@admin_required
@require_POST
def dashboard_metadata_delete(request, pk: int):
    """Delete page metadata"""
    metadata = get_object_or_404(PageMetadata, pk=pk)
    page_name = metadata.page_name
    metadata.delete()
    messages.success(request, f"Metadata for '{page_name}' has been deleted.")
    return redirect("dashboard_metadata_list")


@admin_required
def dashboard_metadata_upload_csv(request):
    """Upload CSV file with URLs and auto-generate metadata using AI"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if it's a CSV file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a CSV file.")
            return redirect("dashboard_metadata_list")
        
        try:
            import csv
            import io
            
            # Read CSV content
            csv_content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Get column names (case-insensitive)
            fieldnames_lower = {name.lower(): name for name in csv_reader.fieldnames or []}
            
            # Find URL column (try multiple variations)
            url_column = None
            for possible in ['url_path', 'page url', 'url', 'link', 'address']:
                if possible in fieldnames_lower:
                    url_column = fieldnames_lower[possible]
                    break
            
            if not url_column:
                messages.error(request, "CSV must have a 'url_path', 'Page URL', 'URL', or 'Link' column.")
                return redirect("dashboard_metadata_list")
            
            # Find page_name column (optional)
            page_name_column = None
            for possible in ['page_name', 'page name', 'name', 'title']:
                if possible in fieldnames_lower:
                    page_name_column = fieldnames_lower[possible]
                    break
            
            created_count = 0
            skipped_count = 0
            errors = []
            
            def extract_path_from_url(url_input):
                """Extract URL path from full URL or path"""
                if not url_input:
                    return None
                
                url_input = url_input.strip()
                
                # If it's a full URL, extract the path
                if url_input.startswith('http://') or url_input.startswith('https://'):
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(url_input)
                        path = parsed.path
                        # Ensure it starts with /
                        if not path.startswith('/'):
                            path = '/' + path
                        return path
                    except Exception:
                        # If parsing fails, try simple extraction
                        if '/' in url_input:
                            # Find the path after domain
                            parts = url_input.split('/', 3)
                            if len(parts) >= 4:
                                return '/' + parts[3]
                        return None
                
                # If it's already a path, ensure it starts with /
                if not url_input.startswith('/'):
                    return '/' + url_input
                
                return url_input
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header row
                url_input = row.get(url_column, '').strip()
                page_name = row.get(page_name_column, '').strip() if page_name_column else ''
                
                if not url_input:
                    errors.append(f"Row {row_num}: Missing URL in '{url_column}' column")
                    continue
                
                # Extract path from full URL or use as-is if already a path
                url_path = extract_path_from_url(url_input)
                
                if not url_path:
                    errors.append(f"Row {row_num}: Could not extract path from '{url_input}'")
                    continue
                
                # Check if entry already exists
                if PageMetadata.objects.filter(url_path=url_path).exists():
                    skipped_count += 1
                    continue
                
                try:
                    # Generate metadata with AI
                    use_ai = request.POST.get('use_ai', 'on') == 'on'
                    
                    if use_ai:
                        try:
                            ai_metadata = generate_metadata_with_ai(url_path, page_name)
                            meta_title = ai_metadata.get('meta_title', '')
                            meta_description = ai_metadata.get('meta_description', '')
                            meta_keywords = ai_metadata.get('meta_keywords', '')
                        except Exception as ai_error:
                            # Fallback to basic generation if AI fails
                            from .utils.ai_metadata_generator import generate_fallback_metadata
                            fallback = generate_fallback_metadata(url_path, page_name)
                            meta_title = fallback.get('meta_title', '')
                            meta_description = fallback.get('meta_description', '')
                            meta_keywords = fallback.get('meta_keywords', '')
                            messages.warning(request, f"AI generation failed for {url_path}, used fallback")
                    else:
                        # Use basic fallback only
                        from .utils.ai_metadata_generator import generate_fallback_metadata
                        fallback = generate_fallback_metadata(url_path, page_name)
                        meta_title = fallback.get('meta_title', '')
                        meta_description = fallback.get('meta_description', '')
                        meta_keywords = fallback.get('meta_keywords', '')
                    
                    # Create PageMetadata entry
                    PageMetadata.objects.create(
                        url_path=url_path,
                        page_name=page_name or url_path.strip('/').replace('-', ' ').title(),
                        meta_title=meta_title,
                        meta_description=meta_description,
                        meta_keywords=meta_keywords,
                        is_active=True,
                    )
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
            
            # Show results
            if created_count > 0:
                messages.success(request, f"Successfully created {created_count} metadata entries from CSV!")
            if skipped_count > 0:
                messages.info(request, f"Skipped {skipped_count} entries (already exist)")
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
                if len(errors) > 10:
                    messages.error(request, f"... and {len(errors) - 10} more errors")
            
            return redirect("dashboard_metadata_list")
            
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
            return redirect("dashboard_metadata_list")
    
    # GET request - show upload form
    return render(request, "dashboard/metadata_upload_csv.html")


@admin_required
def dashboard_metadata_export_csv(request):
    """Export all metadata as CSV file"""
    import csv
    from datetime import datetime
    
    # Get all metadata
    metadata_list = PageMetadata.objects.order_by("url_path")
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"page_metadata_export_{timestamp}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Page Name', 
        'URL Path', 
        'Meta Title', 
        'Meta Description',
        'Meta Keywords',
        'OG Title',
        'OG Description',
        'OG Image',
        'Is Active',
        'Created',
        'Updated'
    ])
    
    # Write data
    for metadata in metadata_list:
        writer.writerow([
            metadata.page_name,
            metadata.url_path,
            metadata.meta_title or '',
            metadata.meta_description or '',
            metadata.meta_keywords or '',
            metadata.og_title or '',
            metadata.og_description or '',
            metadata.og_image or '',
            'Yes' if metadata.is_active else 'No',
            metadata.created_at.strftime('%Y-%m-%d %H:%M:%S') if metadata.created_at else '',
            metadata.updated_at.strftime('%Y-%m-%d %H:%M:%S') if metadata.updated_at else '',
        ])
    
    return response


@admin_required
def dashboard_metadata_export_pdf(request):
    """Export all metadata as PDF file"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        from datetime import datetime
    except ImportError:
        messages.error(request, "ReportLab library not installed. Run: pip install reportlab")
        return redirect("dashboard_metadata_list")
    
    # Get all metadata
    metadata_list = PageMetadata.objects.order_by("url_path")
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"page_metadata_export_{timestamp}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=20,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12,
    )
    
    # Title
    elements.append(Paragraph("Page Metadata Export", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    total_pages = metadata_list.count()
    with_metadata = sum(1 for m in metadata_list if m.meta_title)
    elements.append(Paragraph(f"Total Pages: {total_pages} | With Metadata: {with_metadata}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Create table data
    table_data = []
    
    # Header
    table_data.append([
        Paragraph('<b>Page Name</b>', styles['Normal']),
        Paragraph('<b>URL</b>', styles['Normal']),
        Paragraph('<b>Title</b>', styles['Normal']),
        Paragraph('<b>Status</b>', styles['Normal']),
    ])
    
    # Rows
    for metadata in metadata_list:
        status = '✓ Active' if metadata.is_active else 'Inactive'
        status_color = colors.green if metadata.is_active else colors.grey
        status_text = f'<font color="{status_color}">{status}</font>'
        
        # Truncate long titles for table display
        title = metadata.meta_title[:60] + '...' if metadata.meta_title and len(metadata.meta_title) > 60 else (metadata.meta_title or 'No title')
        
        table_data.append([
            Paragraph(metadata.page_name, styles['Normal']),
            Paragraph(metadata.url_path, styles['Normal']),
            Paragraph(title, styles['Normal']),
            Paragraph(status_text, styles['Normal']),
        ])
    
    # Create table
    table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 3*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add detailed information section
    elements.append(Paragraph("Detailed Information", heading_style))
    
    for metadata in metadata_list:
        if metadata.meta_title:  # Only show pages with metadata
            elements.append(Paragraph(f"<b>{metadata.page_name}</b>", styles['Heading3']))
            elements.append(Paragraph(f"URL: {metadata.url_path}", styles['Normal']))
            
            if metadata.meta_title:
                elements.append(Paragraph(f"<b>Meta Title:</b> {metadata.meta_title}", styles['Normal']))
            if metadata.meta_description:
                elements.append(Paragraph(f"<b>Meta Description:</b> {metadata.meta_description}", styles['Normal']))
            if metadata.meta_keywords:
                elements.append(Paragraph(f"<b>Keywords:</b> {metadata.meta_keywords}", styles['Normal']))
            
            elements.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(elements)
    
    return response


# --------------------------------------------------------------------------------------
# Spam Blocking Dashboard Views
# --------------------------------------------------------------------------------------

@admin_required
def dashboard_spam_blocked_emails(request):
    """List blocked emails with ability to add/remove"""
    blocked_emails = BlockedEmail.objects.all().order_by('-blocked_at')
    
    # Pre-fill email from query parameter
    prefill_email = request.GET.get('email', '').strip()
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            email = request.POST.get('email', '').strip().lower()
            reason = request.POST.get('reason', '').strip()
            if email:
                BlockedEmail.objects.get_or_create(
                    email=email,
                    defaults={'reason': reason or 'Manually blocked', 'is_active': True}
                )
                messages.success(request, f"Email {email} has been blocked.")
        elif action == 'toggle':
            email_id = request.POST.get('id')
            try:
                blocked = BlockedEmail.objects.get(id=email_id)
                blocked.is_active = not blocked.is_active
                blocked.save()
                messages.success(request, f"Email {blocked.email} has been {'activated' if blocked.is_active else 'deactivated'}.")
            except BlockedEmail.DoesNotExist:
                messages.error(request, "Email not found.")
        elif action == 'delete':
            email_id = request.POST.get('id')
            try:
                blocked = BlockedEmail.objects.get(id=email_id)
                email = blocked.email
                blocked.delete()
                messages.success(request, f"Email {email} has been removed from blocklist.")
            except BlockedEmail.DoesNotExist:
                messages.error(request, "Email not found.")
        return redirect('dashboard_spam_blocked_emails')
    
    return render(request, "dashboard/spam_blocked_emails.html", {
        "blocked_emails": blocked_emails,
        "prefill_email": prefill_email
    })


@admin_required
def dashboard_spam_blocked_ips(request):
    """List blocked IPs with ability to add/remove"""
    blocked_ips = BlockedIP.objects.all().order_by('-blocked_at')
    
    # Pre-fill IP from query parameter
    prefill_ip = request.GET.get('ip', '').strip()
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            ip_address = request.POST.get('ip_address', '').strip()
            reason = request.POST.get('reason', '').strip()
            if ip_address:
                BlockedIP.objects.get_or_create(
                    ip_address=ip_address,
                    defaults={'reason': reason or 'Manually blocked', 'is_active': True}
                )
                messages.success(request, f"IP {ip_address} has been blocked.")
        elif action == 'toggle':
            ip_id = request.POST.get('id')
            try:
                blocked = BlockedIP.objects.get(id=ip_id)
                blocked.is_active = not blocked.is_active
                blocked.save()
                messages.success(request, f"IP {blocked.ip_address} has been {'activated' if blocked.is_active else 'deactivated'}.")
            except BlockedIP.DoesNotExist:
                messages.error(request, "IP not found.")
        elif action == 'delete':
            ip_id = request.POST.get('id')
            try:
                blocked = BlockedIP.objects.get(id=ip_id)
                ip = blocked.ip_address
                blocked.delete()
                messages.success(request, f"IP {ip} has been removed from blocklist.")
            except BlockedIP.DoesNotExist:
                messages.error(request, "IP not found.")
        return redirect('dashboard_spam_blocked_ips')
    
    return render(request, "dashboard/spam_blocked_ips.html", {
        "blocked_ips": blocked_ips,
        "prefill_ip": prefill_ip
    })


@admin_required
def dashboard_spam_submissions(request):
    """List all form submissions for monitoring"""
    submissions = FormSubmission.objects.all().order_by('-submitted_at')[:500]  # Last 500
    
    # Filtering
    search_query = request.GET.get('search', '').strip()
    if search_query:
        submissions = submissions.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(ip_address__icontains=search_query) |
            Q(message_preview__icontains=search_query)
        )
    
    # Stats
    total_submissions = FormSubmission.objects.count()
    today_submissions = FormSubmission.objects.filter(
        submitted_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    blocked_emails_count = BlockedEmail.objects.filter(is_active=True).count()
    blocked_ips_count = BlockedIP.objects.filter(is_active=True).count()
    
    return render(request, "dashboard/spam_submissions.html", {
        "submissions": submissions,
        "search_query": search_query,
        "stats": {
            "total": total_submissions,
            "today": today_submissions,
            "blocked_emails": blocked_emails_count,
            "blocked_ips": blocked_ips_count,
        }
    })