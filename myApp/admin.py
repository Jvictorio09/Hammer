# myApp/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django import forms
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.text import slugify
import os

from .models import (
    Service, ServiceFeature, ServiceEditorialImage, ServiceProjectImage, Insight,
    ServiceCapability, ServiceProcessStep, ServiceMetric, ServiceFAQ,
    ServicePartnerBrand, ServiceTestimonial,
    CaseStudy, TeamMember,
    MediaAlbum, MediaAsset,
)
from .utils.cloudinary_utils import smart_compress_to_bytes, upload_to_cloudinary, TARGET_BYTES

# -------------------------------------------------------------------
# Service + related inlines
# -------------------------------------------------------------------

class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ("label", "icon_class", "sort_order")


class ServiceEditorialImageInline(admin.TabularInline):
    model = ServiceEditorialImage
    extra = 1
    fields = ("image_url", "caption", "sort_order",)
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.image_url:
            return format_html('<img src="{}" style="height:60px;border-radius:8px;">', obj.image_url)
        return "—"


class ServiceProjectImageInline(admin.TabularInline):
    model = ServiceProjectImage
    extra = 2
    fields = ("thumb_url", "full_url", "caption", "sort_order")
    readonly_fields = ("thumb_preview",)

    def thumb_preview(self, obj):
        if obj and obj.thumb_url:
            return format_html('<img src="{}" style="height:60px;border-radius:8px;">', obj.thumb_url)
        return "—"


class CapabilityInline(admin.TabularInline):
    model = ServiceCapability
    extra = 0
    fields = ("title", "blurb", "icon_class", "sort_order")


class ProcessInline(admin.TabularInline):
    model = ServiceProcessStep
    extra = 0
    fields = ("step_no", "title", "description", "sort_order")


class MetricInline(admin.TabularInline):
    model = ServiceMetric
    extra = 0
    fields = ("value", "label", "sort_order")


class FAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 0
    fields = ("question", "answer", "sort_order")


class BrandInline(admin.TabularInline):
    model = ServicePartnerBrand
    extra = 0
    fields = ("name", "logo_url", "site_url", "sort_order")


class TestimonialInline(admin.TabularInline):
    model = ServiceTestimonial
    extra = 0
    fields = ("author", "role_company", "headshot_url", "quote", "sort_order")


class CaseStudyInline(admin.TabularInline):
    model = CaseStudy
    extra = 0
    fields = (
        "is_featured", "sort_order", "title", "hero_image_url", "summary",
        "scope", "size_label", "timeline_label", "status_label",
        "tags_csv", "cta_url", "hero_preview"
    )
    readonly_fields = ("hero_preview",)

    def hero_preview(self, obj):
        if obj and obj.hero_image_url:
            return format_html('<img src="{}" style="height:60px;border-radius:8px;">', obj.hero_image_url)
        return "—"
    hero_preview.short_description = "Preview"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "sort_order", "updated_at", "hero_preview")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "slug", "eyebrow")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("sort_order", "title")

    fieldsets = (
        ("Basics", {"fields": ("title", "slug", "eyebrow", "is_active", "sort_order")}),
        ("Hero", {"fields": ("hero_headline", "hero_subcopy", "hero_media_url")}),
        ("Stats", {"fields": ("stat_projects", "stat_years", "stat_specialists")}),
        ("Pinned Editorial", {"fields": ("pinned_heading", "pinned_title", "pinned_body_1", "pinned_body_2")}),
        ("Insights", {"fields": ("insights_heading", "insights_subcopy")}),
        ("SEO", {"fields": ("seo_meta_title", "seo_meta_description", "canonical_path")}),
    )

    inlines = [
        ServiceFeatureInline,
        ServiceEditorialImageInline,
        ServiceProjectImageInline,
        CaseStudyInline,
        CapabilityInline, ProcessInline, MetricInline, FAQInline, BrandInline, TestimonialInline,
    ]

    actions = ["activate_services", "deactivate_services"]

    @admin.action(description="Mark selected services as ACTIVE")
    def activate_services(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected services as INACTIVE")
    def deactivate_services(self, request, queryset):
        queryset.update(is_active=False)

    def hero_preview(self, obj):
        url = obj.primary_image_url
        if url:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;">', url)
        return "—"
    hero_preview.short_description = "Hero"


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ("title", "service", "tag", "read_minutes", "published", "published_at")
    list_filter = ("published", "service", "tag")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ("title", "service", "is_featured", "sort_order", "updated_at")
    list_filter = ("is_featured", "service")
    search_fields = ("title", "summary", "tags_csv")
    ordering = ("-is_featured", "sort_order", "title")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display  = ("name", "role", "is_featured", "is_active", "sort_order")
    list_filter   = ("is_featured", "is_active")
    search_fields = ("name", "role", "email")
    ordering      = ("sort_order", "name")


# -------------------------------------------------------------------
# Media library: Admin form + Bulk upload
# -------------------------------------------------------------------

class MediaAssetAdminForm(forms.ModelForm):
    """
    Adds an optional local file upload to the admin form.
    We do NOT store the file; we upload to Cloudinary and persist the URLs only.
    """
    local_file = forms.FileField(
        required=False,
        help_text="Upload one image; >10MB will be compressed, then pushed to Cloudinary."
    )

    class Meta:
        model = MediaAsset
        fields = [
            "album", "title", "slug",
            "secure_url", "web_url", "thumb_url",
            "public_id", "tags_csv",
            "bytes_size", "width", "height", "format",
            "is_active", "sort_order",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        file = self.cleaned_data.get("local_file")

        if file:
            folder = (instance.album.cld_folder if instance.album and instance.album.cld_folder else "uploads").strip("/")
            base_name = instance.slug or slugify(instance.title or file.name.rsplit(".",1)[0])[:120]

            file.seek(0)
            raw = file.read()
            if len(raw) > TARGET_BYTES:
                file.seek(0)
                raw = smart_compress_to_bytes(file)

            # merge album tags + row tags
            tags = []
            if instance.album and instance.album.default_tags:
                tags += [t.strip() for t in instance.album.default_tags.split(",") if t.strip()]
            if instance.tags_csv:
                tags += [t.strip() for t in instance.tags_csv.split(",") if t.strip()]

            result, web_url, thumb_url = upload_to_cloudinary(raw, folder, base_name, tags=tags)

            instance.public_id  = result.get("public_id", "")
            instance.secure_url = result.get("secure_url", "")
            instance.web_url    = web_url
            instance.thumb_url  = thumb_url
            instance.bytes_size = result.get("bytes", 0)
            instance.width      = result.get("width", 0)
            instance.height     = result.get("height", 0)
            instance.format     = result.get("format", "") or result.get("resource_type","")

            if not instance.title:
                instance.title = base_name.replace("-", " ").replace("_", " ").title()
            if not instance.slug:
                instance.slug = slugify(instance.title)[:220]

        if commit:
            instance.save()
        return instance


# Allow <input multiple> in a FileField
class MultiFileInput(forms.FileInput):
    allow_multiple_selected = True


class BulkUploadForm(forms.Form):
    album = forms.ModelChoiceField(
        queryset=MediaAlbum.objects.all(),
        help_text="Choose the album (defines the Cloudinary folder + default tags)."
    )
    extra_tags = forms.CharField(
        required=False,
        help_text="Optional CSV tags to add to every uploaded asset."
    )

    ALLOWED_MIME = {"image/png", "image/jpeg", "image/webp", "image/gif"}
    ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

    def clean(self):
        cleaned = super().clean()
        # File inputs are handled outside the form via request.FILES.getlist("files").
        # We intentionally avoid binding files to this form to bypass single-file validation.
        return cleaned


@admin.register(MediaAlbum)
class MediaAlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "cld_folder", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "description", "cld_folder")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    form = MediaAssetAdminForm
    change_list_template = "admin/myApp/mediaasset/change_list.html"
    list_display = ("title", "album", "is_active", "url", "bytes_size", "updated_at")
    list_filter  = ("album", "is_active")
    search_fields = ("title", "public_id", "secure_url", "web_url", "tags_csv")
    readonly_fields = ("public_id","bytes_size","width","height","format","secure_url","web_url","thumb_url")
    fieldsets = (
        (None, {
            "fields": ("album","title","slug","local_file","is_active","sort_order")
        }),
        ("Cloudinary URLs", {
            "classes": ("collapse",),
            "fields": ("secure_url","web_url","thumb_url","public_id")
        }),
        ("Metadata", {
            "classes": ("collapse",),
            "fields": ("bytes_size","width","height","format","tags_csv")
        }),
    )

    # Add /bulk-upload/ route under MediaAsset admin
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "bulk-upload/",
                self.admin_site.admin_view(self.bulk_upload_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_bulk_upload",
            )
        ]
        return my_urls + urls

    def bulk_upload_view(self, request):
        """
        Custom admin screen: select album + files, compress if needed, upload to Cloudinary,
        create MediaAsset rows, then redirect back to changelist with a summary.
        """
        if request.method == "POST":
            form = BulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                album = form.cleaned_data["album"]
                extra_tags_csv = form.cleaned_data.get("extra_tags") or ""
                extra_tags = [t.strip() for t in extra_tags_csv.split(",") if t.strip()]

                folder = (album.cld_folder or "uploads").strip("/")
                default_tags = []
                if album.default_tags:
                    default_tags += [t.strip() for t in album.default_tags.split(",") if t.strip()]
                if extra_tags:
                    default_tags += extra_tags

                files = request.FILES.getlist("files")
                created = 0
                errors = 0

                for f in files:
                    try:
                        # Server-side validation: MIME and extension
                        ctype = getattr(f, "content_type", "").lower()
                        name_lower = f.name.lower()
                        _, ext = os.path.splitext(name_lower)
                        if ctype not in BulkUploadForm.ALLOWED_MIME or ext not in BulkUploadForm.ALLOWED_EXTS:
                            raise ValueError("Unsupported file type. Allowed: PNG, JPG/JPEG, WEBP, GIF.")

                        base_name = slugify(f.name.rsplit(".",1)[0])[:120]

                        f.seek(0)
                        raw = f.read()
                        if len(raw) > TARGET_BYTES:
                            f.seek(0)
                            raw = smart_compress_to_bytes(f)

                        result, web_url, thumb_url = upload_to_cloudinary(raw, folder, base_name, tags=default_tags)

                        asset = MediaAsset(
                            album = album,
                            title = base_name.replace("-", " ").replace("_", " ").title(),
                            slug  = slugify(base_name)[:220],
                            public_id  = result.get("public_id",""),
                            secure_url = result.get("secure_url",""),
                            web_url    = web_url,
                            thumb_url  = thumb_url,
                            bytes_size = result.get("bytes", 0),
                            width      = result.get("width", 0),
                            height     = result.get("height", 0),
                            format     = result.get("format",""),
                            tags_csv   = ",".join(default_tags),
                            is_active  = True,
                        )
                        asset.save()
                        created += 1
                    except Exception as ex:
                        errors += 1
                        messages.error(request, f"{f.name}: {ex}")

                if created:
                    messages.success(request, f"Uploaded {created} file(s) to '{album.title}'.")
                if errors:
                    messages.warning(request, f"{errors} file(s) failed.")

                # Robust reverse to changelist: admin:<app_label>_<model_name>_changelist
                changelist = reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist")
                return redirect(changelist)
        else:
            form = BulkUploadForm()

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "form": form,
            "title": "Bulk upload media assets",
            "help_text": "Pick an album and select multiple images. Larger files are compressed automatically before upload.",
        }
        return render(request, "admin/bulk_upload_mediaasset.html", context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        bulk_url = reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_bulk_upload")
        extra_context["bulk_upload_url"] = bulk_url
        return super().changelist_view(request, extra_context=extra_context)
