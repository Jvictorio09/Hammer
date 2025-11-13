# Backend Dashboard Implementation – Hammer Services

## Executive Overview
- The dashboards are working because the backend layers align role-based permissions, form orchestration, and persistence across every CRUD surface in `myApp/views.py`.
- Access to each panel is gated by custom decorators (`blog_author_required`, `admin_required`) that wrap Django’s auth stack and profile flags, ensuring only cleared users invoke the view logic.
- Every dashboard route writes against strongly typed models (`Service`, `Insight`, `TeamMember`, `PageHero`, `PageMetadata`, etc.), with model forms and formsets enforcing validation before commits.
- Supporting utilities (metadata AI generation, media upload pipelines, spam filters) are encapsulated in helper modules and invoked by the dashboards to keep logic reusable and testable.

## Access Control & Request Guards
- `blog_author_required` and `admin_required` check authenticated sessions, superuser state, and profile roles, raising `PermissionDenied` for unauthorised hits so dashboard URLs stay concealed behind login. ```79:110:myProject/myApp/views.py
def blog_author_required(view_func):
    ...
        if hasattr(request.user, 'profile'):
            if not (request.user.profile.is_admin or request.user.profile.is_blog_author):
                raise PermissionDenied("You don't have permission to access this page.")
...
def admin_required(view_func):
    ...
            if not request.user.profile.is_admin:
                raise PermissionDenied("You don't have permission to access this page.")
``` 
- The dashboard landing view re-routes pure content authors straight to Insights to avoid exposing service configuration screens unnecessarily. ```1185:1190:myProject/myApp/views.py
@login_required
def dashboard_home(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_blog_author and not request.user.profile.is_admin:
        return redirect('dashboard_insights_list')
    return render(request, "dashboard/home.html")
``` 

## Services CMS Workflow
- `ServiceForm` plus four inline formsets (capabilities, editorial images, case studies, process steps) coordinate creation/edit screens so marketing can shape full service landing pages without touching code. ```1200:1242:myProject/myApp/views.py
def dashboard_service_create(request):
    ...
    if form.is_valid() and capability_formset.is_valid() and image_formset.is_valid() and case_study_formset.is_valid() and process_formset.is_valid():
        service = form.save()
        capability_formset.instance = service
        capability_formset.save()
        image_formset.instance = service
        image_formset.save()
        ...
``` 
- Edit handlers reuse the same formsets, updating or deleting nested records with defensive error handling for legacy slugs and gallery payloads, keeping the dashboard resilient even when content editors reuse titles. ```1246:1334:myProject/myApp/views.py
def dashboard_service_edit(request, pk: int):
    ...
        if form_valid and capability_valid and image_valid and case_study_valid and process_valid:
            service = form.save()
            capability_formset.save()
            image_formset.save()
            case_studies = case_study_formset.save(commit=False)
            for cs in case_studies:
                if not cs.pk:
                    cs.service = service
                try:
                    cs.save()
                except IntegrityError as e:
                    ...
``` 
- Removing a service funnels through a shared confirmation template to guard against accidental deletions, matching the UX used across other dashboards. ```1352:1358:myProject/myApp/views.py
def dashboard_service_delete(request, pk: int):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        service.delete()
        return redirect("dashboard_services_list")
``` 

## Insight Authoring & Versioning
- Insight CRUD routes are wrapped in `blog_author_required`, enabling marketing writers to manage articles while admins can still override publication or delete entries. ```1361:1515:myProject/myApp/views.py
@blog_author_required
def dashboard_insights_list(request):
    insights = Insight.objects.select_related("service", "author").order_by("-published_at", "-created_at")
``` 
- Editor.js JSON blocks are parsed/stored on save, with migrations that auto-convert HTML bodies to blocks and version snapshots via `ContentVersion` so historical drafts survive edits. ```1421:1478:myProject/myApp/views.py
def dashboard_insight_edit(request, pk: int):
    ...
            blocks_json = request.POST.get("blocks", "{}")
            ...
            obj.blocks = blocks_data
            ...
            ContentVersion.objects.create(insight=obj, data=obj.blocks or {})
``` 
- Audit logging is enforced for destructive or status-changing actions, capturing user identity, IP, and contextual metadata before deletes/toggles execute. ```1511:1569:myProject/myApp/views.py
InsightAuditLog.objects.create(
    action='delete',
    insight_id=insight.id,
    ...
    metadata={
        'service_title': insight.service.title,
        'service_slug': insight.service.slug,
    }
)
``` 

## Media & Hero Management
- Dashboard users can import hero configurations per page, including buttons/pills encoded as JSON; fallback parsing accepts comma-separated strings so editors aren’t blocked by malformed payloads. ```2215:2319:myProject/myApp/views.py
def dashboard_hero_create(request):
    ...
    buttons_json = request.POST.get('buttons', '[]')
    try:
        buttons = json.loads(buttons_json)
    except json.JSONDecodeError:
        buttons = []
    ...
``` 
- `gallery_api_images` exposes a JSON feed of `MediaAsset` instances for the media picker dialog, returning Cloudinary URLs, album metadata, and dimensions to drive the front-end modal. ```1623:1642:myProject/myApp/views.py
def gallery_api_images(request):
    images = MediaAsset.objects.filter(is_active=True).select_related('album').order_by('-created_at')
    image_data = []
    for asset in images:
        image_data.append({
            'id': asset.id,
            'title': asset.title,
            'secure_url': asset.secure_url,
            'web_url': asset.web_url,
            ...
``` 
- Bulk Google Drive → Cloudinary uploads run server-side, compressing assets, persisting metadata, and returning success/error arrays so dashboards can give editors granular feedback. ```2000:2056:myProject/myApp/views.py
for result in results:
    if result['success']:
        ...
        asset = MediaAsset.objects.create(
            album=album,
            title=title,
            public_id=result['public_id'],
            secure_url=cloud_result.get('secure_url', ''),
            ...
``` 

## Metadata Automation & SEO Controls
- Metadata dashboards (list/create/edit/delete) give admins full CRUD while computing coverage stats so gaps are visible at a glance. ```2338:2356:myProject/myApp/views.py
metadata_list = PageMetadata.objects.order_by("url_path")
total_pages = metadata_list.count()
with_metadata = sum(1 for m in metadata_list if m.meta_title)
missing_metadata = total_pages - with_metadata
``` 
- CSV upload uses `generate_metadata_with_ai` with fallbacks, column auto-detection, duplicate skipping, and row-level error aggregation, which is why editors can safely batch import dozens of URLs. ```2419:2567:myProject/myApp/views.py
if use_ai:
    try:
        ai_metadata = generate_metadata_with_ai(url_path, page_name)
        ...
    except Exception as ai_error:
        from .utils.ai_metadata_generator import generate_fallback_metadata
        ...
``` 
- Export endpoints serve CSV and styled PDF reports, empowering ops to circulate SEO states externally without direct database access. ```2578:2752:myProject/myApp/views.py
response = HttpResponse(content_type='text/csv')
...
writer.writerow([
    'Page Name',
    'URL Path',
    ...
``` 

## Team & User Administration
- `TeamMemberForm` encapsulates labels, placeholders, and validation for team entries, and the associated CRUD views ensure marketing staff can maintain About-page rosters while the API surface stays consistent. ```781:806:myProject/myApp/views.py
class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'role', 'bio', 'photo_url', 'email', 'linkedin_url', 'is_active', 'is_featured', 'sort_order']
``` 
- Admin-only user management wraps Django’s `UserCreationForm`, updates profile roles, and blocks superuser deletion, keeping role assignments aligned with the decorators described earlier. ```2069:2141:myProject/myApp/views.py
@admin_required
def dashboard_user_create(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'user')
        if form.is_valid():
            user = form.save()
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.save()
``` 

## Spam Mitigation & Audit Dashboards
- Dedicated views manage blocked emails/IPs using toggles and creation flows, all tied into the same template language for consistent UX. ```2760:2846:myProject/myApp/views.py
if action == 'add':
    email = request.POST.get('email', '').strip().lower()
    ...
    BlockedEmail.objects.get_or_create(
        email=email,
        defaults={'reason': reason or 'Manually blocked', 'is_active': True}
    )
``` 
- A submissions dashboard lists up to 500 recent form entries with search, daily stats, and counts of active blocklists, giving support teams the context needed to respond or blacklist. ```2849:2881:myProject/myApp/views.py
submissions = FormSubmission.objects.all().order_by('-submitted_at')[:500]
...
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
``` 

## Supporting Utilities & Shared Logic
- Contact intake uses a Django form with honeypot field; validation hooks feed the spam detection helpers (`record_submission`, `validate_contact_submission`) that populate the dashboards above.
- `send_email_resend` centralises transactional email dispatch (subject/body/tags), keeping asynchronous notifications consistent across dashboard-triggered actions.
- AI metadata helpers (`myApp/utils/ai_metadata_generator.py`) infer context from URL paths, enforce char limits, and gracefully degrade to static copy—this module underpins the CSV ingestion described earlier.

## Operational Confidence
- Because the backend orchestrates authentication, validation, audit logging, and helper services around each dashboard, the admin experience remains stable even under concurrent edits.
- The dashboards are working as intended: editors can safely manage content, SEO, team bios, heroes, and spam controls within permission boundaries, while the system audits destructive actions and keeps metadata synchronised site-wide.


