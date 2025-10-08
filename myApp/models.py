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
    hero_media_url = models.URLField(blank=True)  # <- Cloudinary URL (optional)
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
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)


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

