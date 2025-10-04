# myApp/admin.py
from django.contrib import admin
from .models import (
    Service, ServiceFeature, ServiceEditorialImage, ServiceProjectImage, Insight
)


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ("label", "icon_class", "sort_order")


class ServiceEditorialImageInline(admin.TabularInline):
    model = ServiceEditorialImage
    extra = 1
    fields = ("image_url", "caption", "sort_order")


class ServiceProjectImageInline(admin.TabularInline):
    model = ServiceProjectImage
    extra = 2
    fields = ("thumb_url", "full_url", "caption", "sort_order")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "sort_order", "updated_at")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "slug", "eyebrow")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("sort_order", "title")
    inlines = [ServiceFeatureInline, ServiceEditorialImageInline, ServiceProjectImageInline]

    fieldsets = (
        ("Basics", {"fields": ("title", "slug", "eyebrow", "is_active", "sort_order")}),
        ("Hero", {"fields": ("hero_headline", "hero_subcopy", "hero_media_url")}),
        ("Stats", {"fields": ("stat_projects", "stat_years", "stat_specialists")}),
        ("Pinned Editorial", {"fields": ("pinned_heading", "pinned_title", "pinned_body_1", "pinned_body_2")}),
        ("Insights", {"fields": ("insights_heading", "insights_subcopy")}),
        ("SEO", {"fields": ("seo_meta_title", "seo_meta_description", "canonical_path")}),
    )

    actions = ["activate_services", "deactivate_services"]

    @admin.action(description="Mark selected services as ACTIVE")
    def activate_services(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected services as INACTIVE")
    def deactivate_services(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ("title", "service", "tag", "read_minutes", "published", "published_at")
    list_filter = ("published", "service", "tag")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
