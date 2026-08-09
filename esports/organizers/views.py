from decimal import Decimal, InvalidOperation
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from matches import services
from matches.models import (
    Match, Tournament, TournamentRegistration, TournamentTeam,
)
from . import notifications
from .forms import OrganizerSignUpForm, TeamRegistrationForm, TournamentForm
from .models import Game, Organizer, TournamentPayment
from .payments import PaymentError, get_gateway


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
        if new_status not in valid:
            messages.error(request, "Unknown status.")
        elif new_status == Tournament.STATUS_OPEN and not _payment_settled(tournament):
            # The "rent": can't go live until the per-tournament fee is paid.
            messages.error(
                request,
                "Pay the tournament fee before opening registration.",
            )
        else:
            tournament.status = new_status
            tournament.registration_open = new_status == Tournament.STATUS_OPEN
            tournament.save()
            messages.success(request, f"Status changed to '{valid[new_status]}'.")
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


@organizer_required
def tournament_teams(request, slug):
    """Add / remove the teams entered in a tournament."""
    tournament = _get_owned_tournament(request, slug)
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        if not name:
            messages.error(request, "Team name is required.")
        elif tournament.teams.filter(name__iexact=name).exists():
            messages.error(request, f"'{name}' is already entered.")
        else:
            next_seed = tournament.teams.count() + 1
            TournamentTeam.objects.create(
                tournament=tournament, name=name, seed=next_seed
            )
            messages.success(request, f"Added '{name}'.")
        return redirect("organizer_tournament_teams", slug=tournament.slug)

    return render(
        request,
        "organizers/teams.html",
        {"tournament": tournament, "teams": tournament.teams.all()},
    )


@organizer_required
def team_delete(request, slug, team_id):
    tournament = _get_owned_tournament(request, slug)
    if request.method == "POST":
        team = get_object_or_404(TournamentTeam, pk=team_id, tournament=tournament)
        team.delete()
        messages.success(request, "Team removed.")
    return redirect("organizer_tournament_teams", slug=tournament.slug)


@organizer_required
def generate_fixtures(request, slug):
    """Generate the schedule based on the tournament's format."""
    tournament = _get_owned_tournament(request, slug)
    if request.method == "POST":
        if tournament.teams.count() < 2:
            messages.error(request, "Add at least two teams first.")
            return redirect("organizer_tournament_teams", slug=tournament.slug)

        if tournament.format == Tournament.FORMAT_KNOCKOUT:
            count = services.generate_knockout_fixtures(tournament)
        else:
            # League and (for now) groups both use a single round-robin.
            count = services.generate_league_fixtures(tournament)

        if tournament.status == Tournament.STATUS_DRAFT:
            tournament.status = Tournament.STATUS_ONGOING
            tournament.save(update_fields=["status"])
        messages.success(request, f"Generated {count} matches.")
    return redirect("organizer_tournament_fixtures", slug=tournament.slug)


@organizer_required
def tournament_fixtures(request, slug):
    """List matches grouped by round, with inline score entry."""
    tournament = _get_owned_tournament(request, slug)
    rounds = []
    for rnd in tournament.matchround_set.all().order_by("id"):
        matches = (
            Match.objects.filter(Match_Round=rnd)
            .select_related("home_team", "away_team")
            .order_by("order", "id")
        )
        rounds.append({"round": rnd, "matches": matches})
    return render(
        request,
        "organizers/fixtures.html",
        {"tournament": tournament, "rounds": rounds},
    )


@organizer_required
def record_score(request, slug, match_id):
    tournament = _get_owned_tournament(request, slug)
    match = get_object_or_404(Match, pk=match_id, Match_Tournament=tournament)
    if request.method == "POST":
        if not (match.home_team_id and match.away_team_id):
            messages.error(request, "Both teams must be set before entering a score.")
            return redirect("organizer_tournament_fixtures", slug=tournament.slug)
        try:
            hs = int(request.POST.get("home_score", ""))
            as_ = int(request.POST.get("away_score", ""))
            if hs < 0 or as_ < 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Enter valid, non-negative scores.")
            return redirect("organizer_tournament_fixtures", slug=tournament.slug)

        services.record_result(match, hs, as_)
        if (
            tournament.format == Tournament.FORMAT_KNOCKOUT
            and match.next_match_id is None
            and match.is_played
        ):
            # Final decided -> mark the tournament completed.
            if match.winner is not None and tournament.status != Tournament.STATUS_COMPLETED:
                tournament.status = Tournament.STATUS_COMPLETED
                tournament.save(update_fields=["status"])
        messages.success(request, "Score saved.")
    return redirect("organizer_tournament_fixtures", slug=tournament.slug)


@organizer_required
def tournament_standings(request, slug):
    tournament = _get_owned_tournament(request, slug)
    rows = services.compute_standings(tournament)
    return render(
        request,
        "organizers/standings.html",
        {"tournament": tournament, "rows": rows},
    )


@organizer_required
def registrations(request, slug):
    """Organizer review of incoming team registrations."""
    tournament = _get_owned_tournament(request, slug)
    regs = tournament.registrations.all()
    return render(
        request,
        "organizers/registrations.html",
        {
            "tournament": tournament,
            "registrations": regs,
            "approved_count": tournament.teams.count(),
        },
    )


@organizer_required
def registration_decide(request, slug, reg_id):
    """Approve (-> creates a TournamentTeam) or reject a registration."""
    tournament = _get_owned_tournament(request, slug)
    reg = get_object_or_404(
        TournamentRegistration, pk=reg_id, tournament=tournament
    )
    if request.method != "POST":
        return redirect("organizer_tournament_registrations", slug=tournament.slug)

    action = request.POST.get("action")
    reg.note = (request.POST.get("note") or "").strip()[:200]

    if action == "approve":
        if reg.status == TournamentRegistration.STATUS_APPROVED:
            messages.info(request, "Already approved.")
            return redirect("organizer_tournament_registrations", slug=tournament.slug)
        if tournament.teams.count() >= tournament.max_teams:
            messages.error(
                request,
                f"Tournament is full ({tournament.max_teams} teams). "
                "Increase max teams or reject some registrations.",
            )
            return redirect("organizer_tournament_registrations", slug=tournament.slug)
        if tournament.teams.filter(name__iexact=reg.team_name).exists():
            messages.error(request, f"A team named '{reg.team_name}' already exists.")
            return redirect("organizer_tournament_registrations", slug=tournament.slug)

        team = TournamentTeam.objects.create(
            tournament=tournament,
            name=reg.team_name,
            seed=tournament.teams.count() + 1,
        )
        reg.status = TournamentRegistration.STATUS_APPROVED
        reg.tournament_team = team
        reg.decided_at = timezone.now()
        reg.save()
        notifications.notify_registration_decided(reg)
        messages.success(request, f"Approved '{reg.team_name}'.")

    elif action == "reject":
        reg.status = TournamentRegistration.STATUS_REJECTED
        reg.decided_at = timezone.now()
        # If it had been approved before, remove the created team.
        if reg.tournament_team_id:
            reg.tournament_team.delete()
            reg.tournament_team = None
        reg.save()
        notifications.notify_registration_decided(reg)
        messages.success(request, f"Rejected '{reg.team_name}'.")
    else:
        messages.error(request, "Unknown action.")

    return redirect("organizer_tournament_registrations", slug=tournament.slug)


# --- Payments (fee per tournament, via bKash) ------------------------------

def _payment_settled(tournament):
    payment = getattr(tournament, "payment", None)
    return payment is None or payment.is_settled


def _get_or_create_payment(tournament):
    payment = getattr(tournament, "payment", None)
    if payment is None:
        payment = TournamentPayment.objects.create(
            organizer=tournament.organizer,
            tournament=tournament,
            amount=_tournament_fee(),
        )
    return payment


@organizer_required
def payment_start(request, slug):
    """Begin paying the tournament fee: create a gateway payment and redirect."""
    tournament = _get_owned_tournament(request, slug)
    if request.method != "POST":
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    payment = _get_or_create_payment(tournament)
    if payment.is_settled:
        messages.info(request, "This tournament's fee is already settled.")
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    # A zero (or comped) fee needs no gateway round-trip.
    if payment.amount <= 0:
        payment.status = TournamentPayment.STATUS_WAIVED
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])
        messages.success(request, "No fee due — you're all set.")
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    gateway = get_gateway()
    callback_url = request.build_absolute_uri(
        reverse("organizer_payment_callback", args=[tournament.slug])
    )
    try:
        result = gateway.create_payment(payment, callback_url)
    except PaymentError as exc:
        messages.error(request, f"Could not start payment: {exc}")
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    payment.gateway = gateway.name
    payment.gateway_payment_id = result.gateway_payment_id
    payment.status = TournamentPayment.STATUS_INITIATED
    payment.save(update_fields=["gateway", "gateway_payment_id", "status"])
    return redirect(result.redirect_url)


@organizer_required
def payment_callback(request, slug):
    """Where the payer returns from bKash; verifies and finalizes the payment."""
    tournament = _get_owned_tournament(request, slug)
    payment = _get_or_create_payment(tournament)
    if payment.is_settled:
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    gateway = get_gateway()
    try:
        result = gateway.execute_payment(payment, request.GET)
    except PaymentError as exc:
        payment.status = TournamentPayment.STATUS_FAILED
        payment.save(update_fields=["status"])
        messages.error(request, f"Payment verification failed: {exc}")
        return redirect("organizer_tournament_detail", slug=tournament.slug)

    if result.success:
        payment.status = TournamentPayment.STATUS_PAID
        payment.transaction_id = result.transaction_id
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "transaction_id", "paid_at"])
        messages.success(
            request, "Payment successful — you can now open registration."
        )
    else:
        payment.status = TournamentPayment.STATUS_FAILED
        payment.save(update_fields=["status"])
        messages.error(request, result.message or "Payment was not completed.")
    return redirect("organizer_tournament_detail", slug=tournament.slug)


@organizer_required
def billing(request):
    """All of this organizer's tournament payments."""
    payments = (
        request.user.organizer.payments.select_related("tournament").all()
    )
    return render(request, "organizers/billing.html", {"payments": payments})


# --- Public (no login) -----------------------------------------------------

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


def _public_tournament_or_404(slug):
    """A tournament visible publicly (anything an organizer has published)."""
    return get_object_or_404(
        Tournament.objects.exclude(status=Tournament.STATUS_DRAFT),
        slug=slug,
    )


def public_tournament(request, slug):
    """Public, read-only tournament page with fixtures and standings."""
    tournament = _public_tournament_or_404(slug)
    rounds = []
    for rnd in tournament.matchround_set.all().order_by("id"):
        matches = (
            Match.objects.filter(Match_Round=rnd)
            .select_related("home_team", "away_team")
            .order_by("order", "id")
        )
        rounds.append({"round": rnd, "matches": matches})
    return render(
        request,
        "organizers/public_tournament.html",
        {
            "tournament": tournament,
            "rounds": rounds,
            "standings": services.compute_standings(tournament),
            "team_count": tournament.teams.count(),
        },
    )


def public_register(request, slug):
    """Anonymous team-captain registration for an open tournament."""
    tournament = _public_tournament_or_404(slug)
    if not tournament.registration_open:
        messages.info(request, "Registration is not open for this tournament.")
        return redirect("public_tournament", slug=tournament.slug)
    if tournament.teams.count() >= tournament.max_teams:
        messages.info(request, "This tournament is already full.")
        return redirect("public_tournament", slug=tournament.slug)

    form = TeamRegistrationForm(request.POST or None, tournament=tournament)
    if request.method == "POST" and form.is_valid():
        reg = form.save(commit=False)
        reg.tournament = tournament
        reg.save()
        notifications.notify_new_registration(reg)
        return render(
            request,
            "organizers/public_register_done.html",
            {"tournament": tournament, "registration": reg},
        )
    return render(
        request,
        "organizers/public_register.html",
        {"tournament": tournament, "form": form},
    )
