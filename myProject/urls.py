from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from myApp.sitemaps import sitemaps

urlpatterns = [
    path('admin/', admin.site.urls),
    # Basic auth routes for the dashboard
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include("myApp.urls")),
]