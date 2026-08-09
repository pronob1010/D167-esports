from django import forms
from django.contrib.auth.forms import UserCreationForm

from Accounts.models import User
from matches.models import Tournament, TournamentRegistration
from .models import Organizer


class OrganizerSignUpForm(UserCreationForm):
    """Signs up a new user AND creates their Organizer profile in one step."""
    organization_name = forms.CharField(
        max_length=100,
        help_text="The name teams and players will see (e.g. 'Dhaka Turf League').",
    )
    contact_email = forms.EmailField(required=False)

    class Meta:
        model = User
        # phone is the USERNAME_FIELD; username is still required by the model.
        fields = ("username", "phone")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Organizer.objects.create(
                user=user,
                name=self.cleaned_data["organization_name"],
                contact_email=self.cleaned_data.get("contact_email", ""),
                contact_phone=user.phone,
            )
        return user


class TournamentForm(forms.ModelForm):
    """Create/edit form for an organizer's own tournament.

    Only exposes the platform-facing fields; ownership (organizer) is set in
    the view from the logged-in user, never from user input.
    """
    class Meta:
        model = Tournament
        fields = (
            "Tournament_title",
            "game",
            "format",
            "max_teams",
            "entry_fee",
            "start_date",
            "end_date",
            "about",
        )
        labels = {
            "Tournament_title": "Tournament name",
            "about": "Description",
            "entry_fee": "Team entry fee",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "about": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "End date cannot be before the start date.")
        return cleaned


class TeamRegistrationForm(forms.ModelForm):
    """Public form a team captain fills in to register for a tournament."""
    class Meta:
        model = TournamentRegistration
        fields = (
            "team_name",
            "captain_name",
            "captain_phone",
            "captain_email",
            "roster",
        )
        labels = {
            "captain_email": "Captain email (optional, for updates)",
            "roster": "Players (one per line)",
        }
        widgets = {
            "roster": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, tournament=None, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)

    def clean_team_name(self):
        name = self.cleaned_data["team_name"].strip()
        if self.tournament and self.tournament.registrations.filter(
            team_name__iexact=name
        ).exclude(status=TournamentRegistration.STATUS_REJECTED).exists():
            raise forms.ValidationError(
                "A team with this name has already registered."
            )
        return name
