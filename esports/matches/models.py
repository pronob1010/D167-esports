
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import TextField, related
from teams.models import Team

class SEASON(models.Model):
    SEASON_title = models.CharField(max_length=25)

    def __str__(self):
        return self.SEASON_title 

class MatchRound(models.Model):
    Season = models.ForeignKey(SEASON, on_delete=CASCADE)
    Round_title = models.CharField(max_length=25)

    def __str__(self):
        return  self.Season.SEASON_title +" - "+ self.Round_title

class Match(models.Model):
    Match_Title = models.CharField(max_length=100)
    Match_SEASON = models.ForeignKey(SEASON, on_delete=CASCADE, default=None)
    Match_Round = models.ForeignKey(MatchRound, on_delete=CASCADE, default=None)
    Featured = models.BooleanField(default=False)
    Countdown_Expected = models.BooleanField(default=False)
    TimeDate = models.DateTimeField(null=True, blank=True)
    MatchAbout = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.Match_Title + " - " + self.Match_Round.Round_title + " - " + self.Match_SEASON.SEASON_title
class MatchTeamDetails(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    Match_Point = models.IntegerField(default=0)

from players.models import Player
class PlayersPointTable(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=CASCADE, null=True, blank=True)
    kills = models.PositiveBigIntegerField(default=0)