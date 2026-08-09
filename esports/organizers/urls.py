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
    # Teams, fixtures, scores, standings.
    path(
        "tournaments/<slug:slug>/teams/",
        views.tournament_teams,
        name="organizer_tournament_teams",
    ),
    path(
        "tournaments/<slug:slug>/teams/<int:team_id>/delete/",
        views.team_delete,
        name="organizer_team_delete",
    ),
    path(
        "tournaments/<slug:slug>/generate/",
        views.generate_fixtures,
        name="organizer_generate_fixtures",
    ),
    path(
        "tournaments/<slug:slug>/fixtures/",
        views.tournament_fixtures,
        name="organizer_tournament_fixtures",
    ),
    path(
        "tournaments/<slug:slug>/fixtures/<int:match_id>/score/",
        views.record_score,
        name="organizer_record_score",
    ),
    path(
        "tournaments/<slug:slug>/standings/",
        views.tournament_standings,
        name="organizer_tournament_standings",
    ),
    path(
        "tournaments/<slug:slug>/registrations/",
        views.registrations,
        name="organizer_tournament_registrations",
    ),
    path(
        "tournaments/<slug:slug>/registrations/<int:reg_id>/decide/",
        views.registration_decide,
        name="organizer_registration_decide",
    ),
    # Public pages (no login).
    path("o/<slug:slug>/", views.public_organizer, name="public_organizer"),
    path("t/<slug:slug>/", views.public_tournament, name="public_tournament"),
    path("t/<slug:slug>/register/", views.public_register, name="public_register"),
]
