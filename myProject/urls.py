from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.contrib.auth import views as auth_views
from myApp import views
from myApp.sitemaps import (
    StaticViewSitemap,
    ServiceSitemap,
    InsightSitemap,
    CaseStudySitemap,
    TeamSitemap,
)

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'insights': InsightSitemap,
    'case_studies': CaseStudySitemap,
    'team': TeamSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    # Basic auth routes for the dashboard
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    # SEO files
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('llms.txt', views.llms_txt, name='llms_txt'),  # Returns 404 - not needed
    path('', include("myApp.urls")),
]