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

    # Legacy route → redirect to the canonical service slug you seeded
    # Adjust "landscape-design-build" if you use a different slug
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

    # (Optional) your static test page
    path("test-look/", views.landscape, name="landscape_test"),

    path("projects/", views.projects_index, name="projects_index"),
    path("projects/<slug:service_slug>/", views.projects_index, name="projects_by_service"),


    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
