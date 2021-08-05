
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import TextField, related
from teams.models import Team
from django.template.defaultfilters import slugify
class SEASON(models.Model):
    SEASON_title = models.CharField(max_length=25)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.SEASON_title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.SEASON_title

class MatchRound(models.Model):
    Season = models.ForeignKey(SEASON, on_delete=CASCADE)
    Round_title = models.CharField(max_length=25)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.Round_title +"-"+ self.Season.SEASON_title 

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.Round_title + self.Season.SEASON_title)
        return super().save(*args, **kwargs)

class MatchGroup(models.Model):
    Season = models.ForeignKey(SEASON, on_delete=CASCADE)
    Round = models.ForeignKey(MatchRound, on_delete=CASCADE)
    Group_title = models.CharField(max_length=25)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.Group_title +"-"+ self.Round.Round_title+"-"+ self.Season.SEASON_title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return  self.Group_title +"-"+ self.Round.Round_title+"-"+ self.Season.SEASON_title

class Match(models.Model):
    Match_Title = models.CharField(max_length=100)
    Match_SEASON = models.ForeignKey(SEASON, on_delete=CASCADE, default=None)
    Match_Round = models.ForeignKey(MatchRound, on_delete=CASCADE, default=None)
    Match_Group = models.ForeignKey(MatchGroup, on_delete=CASCADE, default=None)
    Featured = models.BooleanField(default=False)
    Countdown_Expected = models.BooleanField(default=False)
    TimeDate = models.DateTimeField(null=True, blank=True)
    MatchAbout = models.TextField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.Match_Title + "-" + self.Match_Group.Group_title + "-" + self.Match_Round.Round_title + "-" + self.Match_SEASON.SEASON_title
class RegisteredTeams(models.Model):
    Match = models.ForeignKey(Match, on_delete=CASCADE, null=True, blank=True)
    Team = models.ForeignKey(Team, on_delete=CASCADE, null=True, blank=True)
    Win = models.BooleanField(default=False, null=True, blank=True)
    Placement_Point = models.IntegerField(default=0)
    total_Point = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.Team.TeamName+ "-"+ self.Match.Match_Title +"-"+ self.Match.Match_Group.Group_title +"-"+self.Match.Match_Round.Round_title +"-"+self.Match.Match_SEASON.SEASON_title
    
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