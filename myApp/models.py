# myApp/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Service(TimeStamped):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    eyebrow = models.CharField(max_length=80, blank=True)
    hero_headline = models.CharField(max_length=250)
    hero_subcopy = models.TextField(blank=True)
    hero_media_url = models.URLField(blank=True)  # <- Original/full Cloudinary URL
    hero_cropped_url = models.URLField(blank=True, help_text="Cropped hero image (21:9 aspect ratio)")
    hero_image_position = models.CharField(max_length=50, default='50% 40%',
                                          help_text="CSS background-position for hero image (e.g., '50% 40%')")
    stat_projects = models.CharField(max_length=20, default="650+")
    stat_years = models.CharField(max_length=20, default="20+")
    stat_specialists = models.CharField(max_length=20, default="1000+")
    pinned_heading = models.CharField(max_length=200, blank=True)
    pinned_title = models.CharField(max_length=250, blank=True)
    pinned_body_1 = models.TextField(blank=True)
    pinned_body_2 = models.TextField(blank=True)

    # Optional copy for insights section
    insights_heading = models.CharField(max_length=200, blank=True, help_text="Heading for Insights block on this service page.")
    insights_subcopy = models.CharField(max_length=300, blank=True, help_text="Short description under the Insights heading.")

    # Featured case study for landing page
    featured_case_study = models.ForeignKey('CaseStudy', on_delete=models.SET_NULL, null=True, blank=True, 
                                            related_name='featured_in_service',
                                            help_text="Select which project will be featured on the landing page for this service")

    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    seo_meta_title = models.CharField(max_length=70, blank=True)
    seo_meta_description = models.CharField(max_length=200, blank=True)
    canonical_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title or "service")
        super().save(*args, **kwargs)

    # ---------- NEW: helpers for dynamic section ----------
    @property
    def primary_image_url(self) -> str:
        """
        Returns the hero image to use for the card background.
        Prefer explicit hero_media_url; fallback to first editorial image.
        """
        if self.hero_media_url:
            return self.hero_media_url
        first_editorial = self.editorial_images.order_by("sort_order", "id").values_list("image_url", flat=True).first()
        return first_editorial or ""

    def feature_icons(self, limit: int = 4):
        """
        Returns up to `limit` (icon_class, label) tuples for bullet points.
        """
        qs = self.features.order_by("sort_order", "id").values_list("icon_class", "label")[:limit]
        return list(qs)

    from django.urls import reverse

    def get_absolute_url(self):
        if self.canonical_path:
            return self.canonical_path
        if self.slug:
            return reverse("service_detail", kwargs={"slug": self.slug})
        return reverse("service_index")


class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="features")
    icon_class = models.CharField(max_length=80, default="fa-solid fa-seedling")
    label = models.CharField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • {self.label}"


class ServiceEditorialImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="editorial_images")
    image_url = models.URLField()
    caption = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • editorial {self.pk}"


# ServiceProjectImage is deprecated - images are now stored directly in CaseStudy
# Keeping model for backwards compatibility but no longer used
class ServiceProjectImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="project_images")
    case_study = models.ForeignKey('CaseStudy', on_delete=models.SET_NULL, related_name="legacy_images", null=True, blank=True, help_text="Legacy field - images now in CaseStudy")
    thumb_url = models.URLField(blank=True)
    full_url = models.URLField(blank=True)
    caption = models.CharField(max_length=140, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • project {self.pk}"


class ServiceCapability(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='capabilities')
    title = models.CharField(max_length=120)
    blurb = models.CharField(max_length=240, blank=True)
    icon_class = models.CharField(max_length=80, default="fa-solid fa-circle-check")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • {self.title}"


class ServiceProcessStep(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='process_steps')
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True)
    step_no = models.PositiveSmallIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "step_no", "id"]

    def __str__(self):
        return f"{self.service.title} • Step {self.step_no}: {self.title}"


class ServiceMetric(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='metrics')
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=40)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • {self.value} {self.label}"


class ServiceFAQ(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=220)
    answer = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • Q: {self.question[:40]}"


class ServicePartnerBrand(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='partner_brands')
    name = models.CharField(max_length=120)
    logo_url = models.URLField(blank=True)
    site_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • Brand: {self.name}"


class ServiceTestimonial(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='testimonials')
    author = models.CharField(max_length=120)
    role_company = models.CharField(max_length=160, blank=True)
    quote = models.TextField()
    headshot_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        who = f"{self.author} ({self.role_company})" if self.role_company else self.author
        return f"{self.service.title} • {who}"


class Insight(TimeStamped):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="insights")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    cover_image_url = models.URLField(blank=True)
    tag = models.CharField(max_length=40, blank=True)
    excerpt = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    blocks = models.JSONField(default=dict, blank=True)
    read_minutes = models.PositiveSmallIntegerField(default=4)
    published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True, help_text="Inactive insights are not shown in public views")
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_insights')

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug from title if empty or invalid (like "-")
        if not self.slug or self.slug.strip() == "-" or not self.slug.strip():
            base_slug = slugify(self.title)[:220]
            if not base_slug:
                # Fallback if title doesn't generate a valid slug
                base_slug = "insight"
            
            # Ensure slug is unique
            original_slug = base_slug
            counter = 1
            
            # Check for existing insights with this slug (exclude current instance if updating)
            if self.pk:
                existing = Insight.objects.filter(slug=base_slug).exclude(pk=self.pk)
            else:
                existing = Insight.objects.filter(slug=base_slug)
            
            # If slug exists, append number until unique
            while existing.exists():
                counter += 1
                # Keep total length under 220 chars (account for "-{counter}")
                max_base_length = 220 - len(str(counter)) - 1
                base_slug = f"{original_slug[:max_base_length]}-{counter}"
                if self.pk:
                    existing = Insight.objects.filter(slug=base_slug).exclude(pk=self.pk)
                else:
                    existing = Insight.objects.filter(slug=base_slug)
                
                # Safety limit
                if counter > 10000:
                    break
            
            self.slug = base_slug
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the detail page URL for this insight"""
        return reverse('insight_detail', kwargs={'slug': self.slug})


class ContentVersion(TimeStamped):
    insight = models.ForeignKey(Insight, related_name="versions", on_delete=models.CASCADE)
    data = models.JSONField(default=dict)


class InsightAuditLog(models.Model):
    """Audit trail for insight deletions and other actions"""
    ACTION_CHOICES = [
        ('delete', 'Delete'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('activate', 'Activate'),
        ('deactivate', 'Deactivate'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    insight_id = models.PositiveIntegerField(help_text="ID of the insight (may be deleted)")
    insight_slug = models.SlugField(max_length=220, blank=True, help_text="Slug of the insight")
    insight_title = models.CharField(max_length=200, help_text="Title of the insight")
    actor = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    actor_username = models.CharField(max_length=150, blank=True, help_text="Username at time of action")
    actor_email = models.EmailField(blank=True, help_text="Email at time of action")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the actor")
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional context data")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.insight_title} by {self.actor_username or 'Unknown'} at {self.timestamp}"


class UserProfile(models.Model):
    """Extended user profile with role information"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('blog_author', 'Blog Author'),
        ('user', 'Regular User'),
    ]
    
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def is_blog_author(self):
        return self.role == 'blog_author'
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser


# myApp/models.py (append near your other models)
from django.db import models
from django.utils.text import slugify

class CaseStudy(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='case_studies')
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    hero_image_url = models.URLField(help_text="Cloudinary URL for the featured banner image")
    
    # Project images (stored inline with case study)
    thumb_url = models.URLField(blank=True, help_text="Thumbnail for service page gallery")
    full_url = models.URLField(blank=True, help_text="Full resolution image")
    
    # Gallery images (JSON array of {full: url, thumb: url} objects)
    gallery_urls = models.JSONField(default=list, blank=True, help_text="Array of gallery image objects with full and thumb URLs")
    
    summary = models.TextField(blank=True, help_text="Short teaser for the projects section")
    description = models.TextField(blank=True, help_text="Full project description and story")
    completion_date = models.DateField(null=True, blank=True, help_text="When was the project completed?")

    # Facts shown in the 2x2 grid
    scope = models.CharField(max_length=100, blank=True, default="Design + Build")
    size_label = models.CharField(max_length=100, blank=True, default="")
    timeline_label = models.CharField(max_length=100, blank=True, default="")
    status_label = models.CharField(max_length=100, blank=True, default="Completed")

    # CSV tags rendered as pills (e.g., "Architecture, Interior Fit-Out, Joinery, Landscape")
    tags_csv = models.CharField(max_length=300, blank=True)

    # Control where this appears
    is_featured = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    # Optional deep link (detail page, PDF, gallery, etc.)
    cta_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "sort_order", "title"]

    def __str__(self):
        return f"{self.title} • {self.service.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240]
        super().save(*args, **kwargs)

    @property
    def tags_list(self):
        if not self.tags_csv:
            return []
        return [t.strip() for t in self.tags_csv.split(",") if t.strip()]
    
    def get_absolute_url(self):
        """Return the detail page URL for this case study"""
        return reverse('case_study_detail', kwargs={'slug': self.slug})


# myApp/models.py
from django.db import models
from django.utils.text import slugify

class TeamMember(models.Model):
    name         = models.CharField(max_length=120)
    slug         = models.SlugField(max_length=140, unique=True, blank=True)
    role         = models.CharField(max_length=160, blank=True)
    bio          = models.TextField(blank=True)
    photo_url    = models.URLField(blank=True, help_text="Cloudinary (or any) image URL")
    email        = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)

    is_active    = models.BooleanField(default=True, db_index=True)
    is_featured  = models.BooleanField(default=True, db_index=True)  # show on About by default
    sort_order   = models.PositiveIntegerField(default=0, db_index=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self): return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("team_detail", kwargs={"slug": self.slug})

    @property
    def photo_card(self):
        if not self.photo_url:
            return ""
        if "res.cloudinary.com" in self.photo_url and "/upload/" in self.photo_url:
            return self.photo_url.replace(
                "/upload/",
                "/upload/f_auto,q_auto,c_fill,g_face,w_800,h_1000/"
            )
        return self.photo_url
    


# myApp/models.py (append)
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class MediaAlbum(models.Model):
    """Logical grouping + default Cloudinary folder."""
    title       = models.CharField(max_length=160)
    slug        = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True)
    cld_folder  = models.CharField(
        max_length=200, blank=True,
        help_text="Cloudinary folder (e.g., projects/dubai_hills). If blank, uses 'uploads'."
    )
    default_tags = models.CharField(
        max_length=300, blank=True,
        help_text="CSV tags to apply to assets uploaded through Admin."
    )

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:180]
        super().save(*args, **kwargs)


class MediaAsset(models.Model):
    """
    URL-only asset row. Admin can upload a local file once; we store URLs returned by Cloudinary.
    """
    album       = models.ForeignKey(MediaAlbum, null=True, blank=True, on_delete=models.SET_NULL, related_name="assets")
    title       = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True, blank=True)

    # Cloudinary identifiers/URLs
    public_id   = models.CharField(max_length=240, blank=True, db_index=True)
    secure_url  = models.URLField(blank=True, help_text="Original delivery URL (secure)")
    web_url     = models.URLField(blank=True, help_text="f_auto,q_auto variant for web use")
    thumb_url   = models.URLField(blank=True, help_text="Small thumbnail variant")

    # Optional metadata
    bytes_size  = models.PositiveIntegerField(default=0)
    width       = models.PositiveIntegerField(default=0)
    height      = models.PositiveIntegerField(default=0)
    format      = models.CharField(max_length=20, blank=True)
    tags_csv    = models.CharField(max_length=300, blank=True)

    is_active   = models.BooleanField(default=True, db_index=True)
    sort_order  = models.PositiveIntegerField(default=0, db_index=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["album__title", "sort_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:220]
            self.slug = base_slug
            
            # Ensure slug is unique by appending a number if needed
            counter = 1
            while MediaAsset.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"[:220]
                counter += 1
        super().save(*args, **kwargs)

    # Handy accessors
    @property
    def url(self):
        return self.web_url or self.secure_url

    def get_absolute_url(self):
        # Optional detail page (add a URL if you plan to expose it)
        return reverse("mediaasset_detail", kwargs={"slug": self.slug}) if self.slug else "#"


class PageHero(models.Model):
    """
    Dynamic hero section content for each page.
    Allows superusers to customize hero images and text per page.
    """
    PAGE_CHOICES = [
        ('home', 'Home'),
        ('about', 'About'),
        ('services', 'Services'),
        ('projects', 'Projects'),
        ('insights', 'Insights'),
        ('contact', 'Contact'),
    ]
    
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True, db_index=True, 
                           help_text="Which page this hero applies to")
    title = models.CharField(max_length=200, help_text="Internal title for identification")
    
    # Hero content
    eyebrow = models.CharField(max_length=100, blank=True, 
                              help_text="Small text above headline (e.g., 'Dubai • Design & Build')")
    headline = models.CharField(max_length=250, 
                               help_text="Main hero headline")
    subtext = models.TextField(blank=True, 
                              help_text="Supporting text below headline")
    
    # Hero image
    hero_image_url = models.URLField(blank=True, 
                                     help_text="Cloudinary URL for hero background image")
    image_position = models.CharField(max_length=50, default='50% 50%',
                                     help_text="CSS background-position (e.g., '50% 50%', '50% 30%')")
    
    # Call-to-action buttons (stored as JSON for flexibility)
    buttons = models.JSONField(default=list, blank=True,
                              help_text="Array of button objects: [{text, url, style}, ...]")
    
    # Feature pills below CTA buttons
    pills = models.JSONField(default=list, blank=True,
                            help_text="Array of pill text: ['pill 1', 'pill 2', ...]")
    
    # Control
    is_active = models.BooleanField(default=True, db_index=True,
                                   help_text="Set to false to temporarily disable")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['page']
        verbose_name = 'Page Hero'
        verbose_name_plural = 'Page Heroes'
    
    def __str__(self):
        return f"{self.get_page_display()} Hero - {self.title}"
    
    @classmethod
    def get_hero_for_page(cls, page_identifier):
        """
        Get active hero content for a page, with fallback to default.
        """
        try:
            return cls.objects.get(page=page_identifier, is_active=True)
        except cls.DoesNotExist:
            return None


class PageMetadata(models.Model):
    """
    Store SEO metadata for pages that don't have it built into their models.
    This allows managing meta tags for all URLs including static pages.
    """
    url_path = models.CharField(
        max_length=500, 
        unique=True,
        help_text="URL path (e.g., '/about/', '/projects/', '/landscape/')"
    )
    page_name = models.CharField(
        max_length=200,
        help_text="Human-readable name for this page"
    )
    meta_title = models.CharField(
        max_length=160,
        blank=True,
        help_text="Page title for SEO (recommended: 50-70 characters, max 160)"
    )
    meta_description = models.CharField(
        max_length=320,
        blank=True,
        help_text="Meta description for SEO (recommended: 150-160 characters, max 320)"
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional keywords (comma-separated)"
    )
    og_title = models.CharField(
        max_length=160,
        blank=True,
        help_text="Open Graph title for social sharing (recommended: 50-70 characters, max 160)"
    )
    og_description = models.CharField(
        max_length=400,
        blank=True,
        help_text="Open Graph description for social sharing (recommended: 200-300 characters, max 400)"
    )
    og_image = models.URLField(
        blank=True,
        help_text="Open Graph image URL for social sharing"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['url_path']
        verbose_name = 'Page Metadata'
        verbose_name_plural = 'Pages Metadata'
    
    def __str__(self):
        return f"{self.page_name} - {self.url_path}"


# --------------------------------------------------------------------------------------
# Spam Blocking Models
# --------------------------------------------------------------------------------------

class BlockedEmail(models.Model):
    """Blocked email addresses that should be rejected"""
    email = models.EmailField(unique=True, db_index=True)
    reason = models.CharField(max_length=255, blank=True, help_text="Why this email was blocked")
    blocked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        ordering = ['-blocked_at']
        verbose_name = 'Blocked Email'
        verbose_name_plural = 'Blocked Emails'
    
    def __str__(self):
        return f"{self.email} (blocked: {self.blocked_at.strftime('%Y-%m-%d')})"


class BlockedIP(models.Model):
    """Blocked IP addresses that should be rejected"""
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    reason = models.CharField(max_length=255, blank=True, help_text="Why this IP was blocked")
    blocked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        ordering = ['-blocked_at']
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'
    
    def __str__(self):
        return f"{self.ip_address} (blocked: {self.blocked_at.strftime('%Y-%m-%d')})"


class FormSubmission(models.Model):
    """Track form submissions for rate limiting and spam detection"""
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=120)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Store submission data for analysis
    service = models.CharField(max_length=100, blank=True)
    message_preview = models.CharField(max_length=200, blank=True, help_text="First 200 chars of message")
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['email', 'submitted_at']),
            models.Index(fields=['ip_address', 'submitted_at']),
        ]
        verbose_name = 'Form Submission'
        verbose_name_plural = 'Form Submissions'
    
    def __str__(self):
        return f"{self.email} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"


class JobPosting(TimeStamped):
    """Job posting/position available"""
    POSITION_CHOICES = [
        ('', 'Select Position'),
        ('Landscape Designer', 'Landscape Designer'),
        ('Interior Designer', 'Interior Designer'),
        ('Project Manager', 'Project Manager'),
        ('Site Engineer', 'Site Engineer'),
        ('Architect', 'Architect'),
        ('Sales Executive', 'Sales Executive'),
        ('Accountant', 'Accountant'),
        ('Admin Assistant', 'Admin Assistant'),
        ('Facility Manager', 'Facility Manager'),
        ('Other', 'Other'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('Landscape', 'Landscape'),
        ('Interior & Fit-Out', 'Interior & Fit-Out'),
        ('FM', 'FM'),
        ('Admin', 'Admin'),
        ('Finance', 'Finance'),
        ('Sales', 'Sales'),
    ]
    
    title = models.CharField(max_length=200, help_text="Job title/position name")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    description = models.TextField(blank=True, help_text="Job description and requirements")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Is this position currently open?")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    
    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.title} ({self.department})" if self.department else self.title


class JobApplication(TimeStamped):
    """Job application submitted by candidates"""
    VISA_STATUS_CHOICES = [
        ('', 'Select Visa Status'),
        ('Visit Visa', 'Visit Visa'),
        ('Employment Visa', 'Employment Visa'),
        ('Residence Visa', 'Residence Visa'),
        ('Student Visa', 'Student Visa'),
        ('No Visa', 'No Visa'),
        ('Other', 'Other'),
    ]
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)
    mobile_number = models.CharField(max_length=20)
    current_location = models.CharField(max_length=200)
    nationality = models.CharField(max_length=100, blank=True)
    visa_status = models.CharField(max_length=50, choices=VISA_STATUS_CHOICES, blank=True)
    
    # Position Details
    position_applied_for = models.ForeignKey(
        JobPosting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications',
        help_text="Position from dropdown"
    )
    position_custom = models.CharField(
        max_length=200,
        blank=True,
        help_text="Custom position if not in dropdown"
    )
    department = models.CharField(max_length=50, blank=True)
    years_of_experience = models.CharField(max_length=50)
    notice_period = models.CharField(max_length=100)
    expected_salary_aed = models.CharField(max_length=50, blank=True)
    
    # Attachments
    cv_resume = models.FileField(
        upload_to='job_applications/cvs/',
        help_text="Upload CV/Resume (PDF/DOC)"
    )
    portfolio_link = models.URLField(blank=True, help_text="Portfolio link or upload")
    portfolio_file = models.FileField(
        upload_to='job_applications/portfolios/',
        blank=True,
        null=True,
        help_text="Portfolio file upload (optional)"
    )
    
    # Short Questions
    why_work_with_us = models.TextField(blank=True, help_text="Why do you want to work with us?")
    relevant_experience = models.TextField(blank=True, help_text="Relevant experience or key project")
    
    # Consent
    information_accurate = models.BooleanField(default=False, help_text="I confirm the information provided is accurate")
    data_processing_consent = models.BooleanField(default=False, help_text="I consent to data processing for recruitment purposes")
    
    # Status tracking
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending Review'),
            ('reviewed', 'Under Review'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired'),
        ],
        default='pending',
        db_index=True
    )
    notes = models.TextField(blank=True, help_text="Internal notes about the candidate")
    
    # IP tracking for spam detection
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
    
    def __str__(self):
        return f"{self.full_name} - {self.position_applied_for or self.position_custom} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def position_display(self):
        """Return the position name (from FK or custom)"""
        return self.position_applied_for.title if self.position_applied_for else self.position_custom