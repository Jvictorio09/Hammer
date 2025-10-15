# myApp/urls.py
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Services index (cards to each service)
    path("services/", views.service_index, name="service_index"),

    # Service detail (canonical)
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),

    # Legacy routes → redirect to the canonical service slugs you seeded
    # Adjust slugs if you use different ones
    
    # Old hammer-services.com URLs - Using actual views for transition period
    path("landscape/", views.legacy_landscape, name="legacy_landscape"),
    path("interior/", views.legacy_interior, name="legacy_interior"),
    path("facility/", views.legacy_facility, name="legacy_facility"),
    path("aboutus/", views.legacy_aboutus, name="legacy_aboutus"),
    path("blogs/", views.legacy_blogs, name="legacy_blogs"),
    
    # Keep existing services/landscape/ redirect for backward compatibility
    path(
        "services/landscape/",
        RedirectView.as_view(
            url=reverse_lazy("service_detail", kwargs={"slug": "landscape-design-build"}),
            permanent=True,
        ),
        name="services_landscape_legacy",
    ),

    # Insights
    path("insights/<slug:slug>/", views.insight_detail, name="insight_detail"),
    
    # Case Studies
    path("case-studies/<slug:slug>/", views.case_study_detail, name="case_study_detail"),

    # (Optional) your static test page
    path("test-look/", views.landscape, name="landscape_test"),

    path("projects/", views.projects_index, name="projects_index"),
    path("projects/<slug:service_slug>/", views.projects_index, name="projects_by_service"),


    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    path("about/", views.about, name="about"),
    path("team/<slug:slug>/", views.team_detail, name="team_detail"),

    # Dashboard (login required at view level)
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    # Services
    path("dashboard/services/", views.dashboard_services_list, name="dashboard_services_list"),
    path("dashboard/services/new/", views.dashboard_service_create, name="dashboard_service_create"),
    path("dashboard/services/<int:pk>/edit/", views.dashboard_service_edit, name="dashboard_service_edit"),
    path("dashboard/services/<int:pk>/delete/", views.dashboard_service_delete, name="dashboard_service_delete"),
    # Insights
    path("dashboard/insights/", views.dashboard_insights_list, name="dashboard_insights_list"),
    path("dashboard/insights/new/", views.dashboard_insight_create, name="dashboard_insight_create"),
    path("dashboard/insights/<int:pk>/edit/", views.dashboard_insight_edit, name="dashboard_insight_edit"),
    path("dashboard/insights/<int:pk>/delete/", views.dashboard_insight_delete, name="dashboard_insight_delete"),
    path("dashboard/insights/<int:pk>/toggle-active/", views.dashboard_insight_toggle_active, name="dashboard_insight_toggle_active"),
    path("dashboard/insights/import/", views.dashboard_insight_import_html, name="dashboard_insight_import"),
    # Editor.js uploader
    path("u/editor-image/", views.editor_image_upload, name="editor_image_upload"),
    # Gallery API
    path("dashboard/gallery/api/images/", views.gallery_api_images, name="gallery_api_images"),
    path("dashboard/gallery/api/upload/", views.gallery_api_upload, name="gallery_api_upload"),
    # Team Members
    path("dashboard/team/", views.dashboard_team_list, name="dashboard_team_list"),
    path("dashboard/team/new/", views.dashboard_team_create, name="dashboard_team_create"),
    path("dashboard/team/<int:pk>/edit/", views.dashboard_team_edit, name="dashboard_team_edit"),
    path("dashboard/team/<int:pk>/delete/", views.dashboard_team_delete, name="dashboard_team_delete"),
    # Users (Admin only)
    path("dashboard/users/", views.dashboard_users_list, name="dashboard_users_list"),
    path("dashboard/users/new/", views.dashboard_user_create, name="dashboard_user_create"),
    path("dashboard/users/<int:pk>/edit/", views.dashboard_user_edit, name="dashboard_user_edit"),
    path("dashboard/users/<int:pk>/delete/", views.dashboard_user_delete, name="dashboard_user_delete"),
]
