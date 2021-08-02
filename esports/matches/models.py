
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import TextField, related
from teams.models import Team

class MatchCategories(models.Model):
    title = models.CharField(max_length=25)

class MatchLevel(models.Model):
    title = models.CharField(max_length=25)

class Match(models.Model):
    MatchTitle = models.CharField(max_length=100, null=True, blank=True)
    MatchCategory = models.ForeignKey(MatchCategories, on_delete=CASCADE, default=None)
    MatchLevel = models.ForeignKey(MatchLevel, on_delete=CASCADE, default=None)
    Featured = models.BooleanField(default=False)
    TimeDate = models.TimeField(null=True, blank=True)
    MatchAbout = models.TextField(max_length=300, null=True, blank=True)

class MatchTeamDetails(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    PointTable = models.IntegerField(default=0)

from players.models import Player
class PlayersPointTable(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=CASCADE, null=True, blank=True)
    point = models.PositiveBigIntegerField(default=0)
