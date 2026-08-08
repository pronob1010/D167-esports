from decimal import Decimal, InvalidOperation
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from matches.models import Tournament
from .forms import OrganizerSignUpForm, TournamentForm
from .models import Game, Organizer, TournamentPayment


def organizer_required(view_func):
    """Allow only logged-in users who have an Organizer profile.

    Combined with the per-organizer querysets in each view, this is what keeps
    one organizer from ever seeing or touching another's data.
    """
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "organizer"):
            messages.info(request, "Create an organizer profile to host tournaments.")
            return redirect("organizer_signup")
        return view_func(request, *args, **kwargs)

    return _wrapped


def _tournament_fee():
    try:
        return Decimal(str(settings.TOURNAMENT_FEE))
    except (InvalidOperation, TypeError):
        return Decimal("0")


def organizer_signup(request):
    """Register a new organizer (creates User + Organizer, then logs in)."""
    if request.user.is_authenticated and hasattr(request.user, "organizer"):
        return redirect("organizer_dashboard")

    form = OrganizerSignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your organizer account is ready.")
        return redirect("organizer_dashboard")
    return render(request, "organizers/signup.html", {"form": form})


@organizer_required
def dashboard(request):
    organizer = request.user.organizer
    # SCOPED: only this organizer's tournaments.
    tournaments = organizer.tournaments.select_related("game", "payment").all()
    context = {
        "organizer": organizer,
        "tournaments": tournaments,
        "total": tournaments.count(),
    }
    return render(request, "organizers/dashboard.html", context)


@organizer_required
def tournament_create(request):
    organizer = request.user.organizer
    form = TournamentForm(request.POST or None)

    # Default the game selector to Turf Football if it isn't chosen yet.
    if not form.is_bound:
        default_game = Game.objects.filter(is_active=True).first()
        if default_game:
            form.fields["game"].initial = default_game.pk

    if request.method == "POST" and form.is_valid():
        tournament = form.save(commit=False)
        tournament.organizer = organizer          # ownership set server-side
        tournament.status = Tournament.STATUS_DRAFT
        tournament.save()

        # Record the per-tournament fee (business model: fee per tournament).
        TournamentPayment.objects.create(
            organizer=organizer,
            tournament=tournament,
            amount=_tournament_fee(),
            status=TournamentPayment.STATUS_PENDING,
        )
        messages.success(
            request,
            "Tournament created as a draft. Open registration when you're ready.",
        )
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    return render(
        request,
        "organizers/tournament_form.html",
        {"form": form, "mode": "create"},
    )


def _get_owned_tournament(request, slug):
    """Fetch a tournament ONLY if it belongs to the requesting organizer."""
    return get_object_or_404(
        Tournament, slug=slug, organizer=request.user.organizer
    )


@organizer_required
def tournament_detail(request, slug):
    tournament = _get_owned_tournament(request, slug)
    payment = getattr(tournament, "payment", None)
    return render(
        request,
        "organizers/tournament_detail.html",
        {"tournament": tournament, "payment": payment},
    )


@organizer_required
def tournament_edit(request, slug):
    tournament = _get_owned_tournament(request, slug)
    form = TournamentForm(request.POST or None, instance=tournament)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tournament updated.")
        return redirect("organizer_tournament_detail", slug=tournament.slug)
    return render(
        request,
        "organizers/tournament_form.html",
        {"form": form, "mode": "edit", "tournament": tournament},
    )


@organizer_required
def tournament_set_status(request, slug):
    """Move a tournament through its lifecycle (draft -> open -> ongoing -> completed)."""
    tournament = _get_owned_tournament(request, slug)
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid = dict(Tournament.STATUS_CHOICES)
        if new_status in valid:
            tournament.status = new_status
            tournament.registration_open = new_status == Tournament.STATUS_OPEN
            tournament.save()
            messages.success(request, f"Status changed to '{valid[new_status]}'.")
        else:
            messages.error(request, "Unknown status.")
    return redirect("organizer_tournament_detail", slug=tournament.slug)


@organizer_required
def tournament_delete(request, slug):
    tournament = _get_owned_tournament(request, slug)
    if request.method == "POST":
        tournament.delete()
        messages.success(request, "Tournament deleted.")
        return redirect("organizer_dashboard")
    return render(
        request,
        "organizers/tournament_confirm_delete.html",
        {"tournament": tournament},
    )


def public_organizer(request, slug):
    """Public page listing an organizer's published (non-draft) tournaments."""
    organizer = get_object_or_404(Organizer, slug=slug, is_active=True)
    tournaments = organizer.tournaments.exclude(
        status=Tournament.STATUS_DRAFT
    ).select_related("game")
    return render(
        request,
        "organizers/public_organizer.html",
        {"organizer": organizer, "tournaments": tournaments},
    )
