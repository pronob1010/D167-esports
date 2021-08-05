from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case
from django.db.models.fields import NullBooleanField

# Create your models here.

from players.models import Player
from django.template.defaultfilters import slugify

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
        return self.player.username + "-"+ self.Team_Name.TeamName