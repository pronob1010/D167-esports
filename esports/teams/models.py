from typing import ClassVar
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case
from django.db.models.fields import NullBooleanField

# Create your models here.

from players.models import Player
from django.template.defaultfilters import slugify, title

class TeamGroup(models.Model):
    title = models.CharField(max_length=25)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title
        
class Team(models.Model):
    TeamName = models.CharField(max_length=50)
    Team_Group = models.ForeignKey(TeamGroup, on_delete=CASCADE, null=True, blank=True)
    Team_image = models.ImageField(upload_to="teams", default = '../static/images/soccer/team-logo5.png', null=True, blank=True)
    TeamAbout = models.TextField(max_length=300, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.TeamName)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.TeamName   
    

class TeamPlayers(models.Model):
    Team_Name = models.ForeignKey(Team, on_delete=CASCADE)
    player = models.ForeignKey(Player, on_delete=CASCADE)
    def __str__(self):
        return self.player.in_game_name +"-"+ self.Team_Name.TeamName

class CentralTeam(models.Model):
    BS_team = models.ForeignKey(Team, on_delete=CASCADE, null=Team, blank=True)
    game = models.CharField(max_length=40)
    Team_Banner = models.ImageField(upload_to="teams", default = '../static/images/147198.jpg', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.BS_team.TeamName+"-"+self.game)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.BS_team.TeamName+"-"+self.game  
class OtherLineUp(models.Model):
    baseteam = models.ForeignKey(CentralTeam, on_delete=CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=CASCADE, null=Team, blank=True)
    
class CentralTeamAchievement(models.Model):
    team = models.ForeignKey(CentralTeam, on_delete=CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    story = models.TextField(max_length=150, null=True, blank=True)
    Banner = models.ImageField(upload_to="teams", default = '../static/images/147198.jpg', null=True, blank=True)
