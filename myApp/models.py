# myApp/models.py
from django.db import models
from django.utils.text import slugify

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
    hero_media_url = models.URLField(blank=True)
    stat_projects = models.CharField(max_length=20, default="650+")
    stat_years = models.CharField(max_length=20, default="20+")
    stat_specialists = models.CharField(max_length=20, default="1000+")
    pinned_heading = models.CharField(max_length=200, blank=True)
    pinned_title = models.CharField(max_length=250, blank=True)
    pinned_body_1 = models.TextField(blank=True)
    pinned_body_2 = models.TextField(blank=True)

    # NEW: optional copy for insights section
    insights_heading = models.CharField(max_length=200, blank=True, help_text="Heading for Insights block on this service page.")
    insights_subcopy = models.CharField(max_length=300, blank=True, help_text="Short description under the Insights heading.")

    seo_meta_title = models.CharField(max_length=70, blank=True)
    seo_meta_description = models.CharField(max_length=160, blank=True)
    canonical_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title or "service")
        super().save(*args, **kwargs)


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


class ServiceProjectImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="project_images")
    thumb_url = models.URLField()
    full_url = models.URLField()
    caption = models.CharField(max_length=140, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.service.title} • project {self.pk}"
    

# myApp/models.py  (append below your existing classes)
from django.db import models

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
    # e.g. "01", "02" for visual labels; or use auto
    step_no = models.PositiveSmallIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "step_no", "id"]

    def __str__(self):
        return f"{self.service.title} • Step {self.step_no}: {self.title}"


class ServiceMetric(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='metrics')
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=40)  # "650+", "98%", "15 yrs"
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


# ===== Insights =====

class Insight(TimeStamped):
    """
    A blog/insight article that can be scoped to a specific Service.
    If service is NULL, treat it as global (optional).
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="insights")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    cover_image_url = models.URLField(blank=True)
    tag = models.CharField(max_length=40, blank=True)  # e.g. "Landscape", "Pre-Con"
    excerpt = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    read_minutes = models.PositiveSmallIntegerField(default=4)
    published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)
