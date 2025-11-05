from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service, Insight, CaseStudy, TeamMember


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return [
            'home',
            'service_index',
            'projects_index',
            'insights_list',
            'about',
            'contact',
            # Legacy URLs that should be indexed
            'legacy_landscape',
            'legacy_interior',
            'legacy_facility',
            'legacy_aboutus',
            'legacy_blogs',
        ]
    
    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """Sitemap for service pages"""
    changefreq = 'monthly'
    priority = 0.9
    
    def items(self):
        return Service.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class InsightSitemap(Sitemap):
    """Sitemap for insight/blog pages"""
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return Insight.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class CaseStudySitemap(Sitemap):
    """Sitemap for case study pages"""
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        # CaseStudy doesn't have is_active field, so return all
        return CaseStudy.objects.all()
    
    def lastmod(self, obj):
        return obj.updated_at


class TeamSitemap(Sitemap):
    """Sitemap for team member pages"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return TeamMember.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at

