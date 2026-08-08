
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import TextField, related
from django.utils import timezone
from teams.models import Team
from django.template.defaultfilters import default, slugify

# class Tournament(models.Model):
#     Tournament_title = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True, null=True, blank=True)

#     def save(self, *args, **kwargs):  # new
#         if not self.slug:
#             self.slug = slugify(self.Tournament_title)
#         return super().save(*args, **kwargs)

#     def __str__(self):
#         return self.Tournament_title
class Tournament(models.Model):
    # --- Multi-tenant / platform fields -----------------------------------
    # Nullable so existing (pre-platform) tournaments keep working; new
    # tournaments created through the organizer dashboard always set these.
    STATUS_DRAFT = "draft"
    STATUS_OPEN = "open"
    STATUS_ONGOING = "ongoing"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_OPEN, "Registration open"),
        (STATUS_ONGOING, "Ongoing"),
        (STATUS_COMPLETED, "Completed"),
    ]

    FORMAT_KNOCKOUT = "knockout"
    FORMAT_LEAGUE = "league"
    FORMAT_GROUPS = "groups"
    FORMAT_CHOICES = [
        (FORMAT_KNOCKOUT, "Knockout"),
        (FORMAT_LEAGUE, "League"),
        (FORMAT_GROUPS, "Groups + knockout"),
    ]

    organizer = models.ForeignKey(
        "organizers.Organizer",
        on_delete=models.CASCADE,
        related_name="tournaments",
        null=True,
        blank=True,
    )
    game = models.ForeignKey(
        "organizers.Game",
        on_delete=models.SET_NULL,
        related_name="tournaments",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    format = models.CharField(
        max_length=12, choices=FORMAT_CHOICES, default=FORMAT_KNOCKOUT
    )
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_teams = models.PositiveIntegerField(default=16)
    registration_open = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    # --- Original fields ---------------------------------------------------
    Tournament_title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    mvp_expected = models.BooleanField(default=False)
    number_of_mvp = models.PositiveIntegerField(default=0)
    about = models.TextField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            base = slugify(self.Tournament_title)
            slug = base
            counter = 2
            # Titles can repeat across organizers, so guarantee a unique slug.
            while Tournament.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.Tournament_title


class MatchRound(models.Model):
    # Tournament = models.ForeignKey(Tournament,on_delete=CASCADE)
    Tournament = models.ForeignKey(Tournament, on_delete=CASCADE)
    Round_title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.Round_title +"-"+self.Tournament.Tournament_title

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.Round_title+"-"+self.Tournament.Tournament_title)
        return super().save(*args, **kwargs)

class MatchGroup(models.Model):
    # Tournament = models.ForeignKey(Tournament,on_delete=CASCADE)
    Tournament = models.ForeignKey(Tournament, on_delete=CASCADE)
    Round = models.ForeignKey(MatchRound, on_delete=CASCADE)
    Group_title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.Group_title +"-"+ self.Round.Round_title+"-"+self.Tournament.Tournament_title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return  self.Group_title +"-"+ self.Round.Round_title+"-"+self.Tournament.Tournament_title

class Match(models.Model):
    Match_Title = models.CharField(max_length=100)
    # Tournament = models.ForeignKey(Tournament,on_delete=CASCADE)
    Match_Tournament = models.ForeignKey(Tournament, on_delete=CASCADE, default=None)
    Match_Round = models.ForeignKey(MatchRound, on_delete=CASCADE, default=None)
    Match_Group = models.ForeignKey(MatchGroup, on_delete=CASCADE, default=None, null=True, blank=True)
    image = models.ImageField(upload_to = "matches", default="../static/images/715035.png", null=True, blank=True)
    Featured = models.BooleanField(default=False)
    Countdown_Expected = models.BooleanField(default=False)
    Use_for_Ranking = models.BooleanField(default=False)
    TimeDate = models.DateTimeField(null=True, blank=True)
    MatchAbout = models.TextField(max_length=300, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    # --- Two-sided fixture result (football etc.) --------------------------
    # Nullable so the legacy battle-royale flow (RegisteredTeams) is untouched.
    home_team = models.ForeignKey(
        "matches.TournamentTeam", on_delete=models.SET_NULL,
        related_name="home_matches", null=True, blank=True,
    )
    away_team = models.ForeignKey(
        "matches.TournamentTeam", on_delete=models.SET_NULL,
        related_name="away_matches", null=True, blank=True,
    )
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    is_played = models.BooleanField(default=False)
    # Knockout bracket wiring: the match the winner advances into.
    next_match = models.ForeignKey(
        "self", on_delete=models.SET_NULL,
        related_name="feeder_matches", null=True, blank=True,
    )
    next_match_slot = models.CharField(max_length=4, blank=True)  # "home" / "away"
    order = models.PositiveIntegerField(default=0)  # ordering within a round

    def _slug_parts(self):
        parts = [self.Match_Title]
        if self.Match_Group_id and self.Match_Group:
            parts.append(self.Match_Group.Group_title)
        if self.Match_Round_id and self.Match_Round:
            parts.append(self.Match_Round.Round_title)
        if self.Match_Tournament_id and self.Match_Tournament:
            parts.append(self.Match_Tournament.Tournament_title)
        return "-".join(p for p in parts if p)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            base = slugify(self._slug_parts())
            slug = base
            counter = 2
            while Match.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        return super().save(*args, **kwargs)

    @property
    def winner(self):
        """Return the winning TournamentTeam, or None for unplayed/draw."""
        if not self.is_played or self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        if self.away_score > self.home_score:
            return self.away_team
        return None  # draw

    def __str__(self):
        return self._slug_parts()


class TournamentTeam(models.Model):
    """A team entered in a specific tournament (tenant-scoped participant).

    Kept separate from the global ``Team`` model so entrants never leak across
    organizers. Public self-registration (Stage C) will create these too.
    """
    tournament = models.ForeignKey(
        Tournament, on_delete=CASCADE, related_name="teams"
    )
    name = models.CharField(max_length=80)
    seed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["seed", "name"]
        unique_together = ("tournament", "name")

    def __str__(self):
        return f"{self.name} ({self.tournament.Tournament_title})"


class RegisteredTeams(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    Win = models.BooleanField(default=False, null=True, blank=True)
    Placement_Point = models.IntegerField(default=0)
    total_Point = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.Team.TeamName+ "-"+ self.Match.Match_Title +"-"+ self.Match.Match_Group.Group_title +"-"+self.Match.Match_Round.Round_title +"-"+self.Match.Match_Tournament.Tournament_title

from players.models import Player
# class PlayersPointTable(models.Model):
#     Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
#     Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
#     player = models.ForeignKey(Player, on_delete=CASCADE, null=True, blank=True)

from teams . models import TeamPlayers
from smart_selects.db_fields import GroupedForeignKey, ChainedForeignKey
class PlayersPointTable(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    teamName = models.ForeignKey(RegisteredTeams, on_delete=CASCADE, null=True, blank=True)
    # team_Name = ChainedForeignKey(
    #     TeamPlayers,
    #     chained_field="Match",
    #     chained_model_field="Team",
    #     show_all=False,
    #     auto_choose=True,
    #     sort=True,
    #     null=True,
    #     blank=True)
    # player = ChainedForeignKey(
    #     TeamPlayers,
    #     chained_field="player",
    #     chained_model_field="player",
    #     show_all=False,
    #     auto_choose=True,
    #     sort=True,
    #     null=True, 
    #     blank=True)

    player = GroupedForeignKey(TeamPlayers, "player", null=True, blank=True)
    # player = models.ForeignKey(Player, on_delete=CASCADE, null=True, blank=True)
    kill_Point = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.teamName.Team.TeamName+"-"+self.Match.Match_Title
