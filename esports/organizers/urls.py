from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.organizer_signup, name="organizer_signup"),
    path("dashboard/", views.dashboard, name="organizer_dashboard"),
    path("tournaments/new/", views.tournament_create, name="organizer_tournament_create"),
    path(
        "tournaments/<slug:slug>/",
        views.tournament_detail,
        name="organizer_tournament_detail",
    ),
    path(
        "tournaments/<slug:slug>/edit/",
        views.tournament_edit,
        name="organizer_tournament_edit",
    ),
    path(
        "tournaments/<slug:slug>/status/",
        views.tournament_set_status,
        name="organizer_tournament_status",
    ),
    path(
        "tournaments/<slug:slug>/delete/",
        views.tournament_delete,
        name="organizer_tournament_delete",
    ),
    # Public, read-only organizer page.
    path("o/<slug:slug>/", views.public_organizer, name="public_organizer"),
]
