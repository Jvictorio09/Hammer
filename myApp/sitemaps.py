# myApp/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, Insight, CaseStudy, TeamMember


class ServiceSitemap(Sitemap):
    """Sitemap for Service pages"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class InsightSitemap(Sitemap):
    """Sitemap for Insight/Blog pages"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Insight.objects.filter(is_active=True, published=True)

    def lastmod(self, obj):
        return obj.published_at or obj.updated_at


class CaseStudySitemap(Sitemap):
    """Sitemap for Case Study/Project pages"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return CaseStudy.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class TeamMemberSitemap(Sitemap):
    """Sitemap for Team Member pages"""
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return TeamMember.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return [
            'home',
            'service_index',
            'insights_list',
            'projects_index',
            'about',
            'contact',
        ]

    def location(self, item):
        return reverse(item)


# Combine all sitemaps
sitemaps = {
    'services': ServiceSitemap,
    'insights': InsightSitemap,
    'case-studies': CaseStudySitemap,
    'team': TeamMemberSitemap,
    'static': StaticViewSitemap,
}

