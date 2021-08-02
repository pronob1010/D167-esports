from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case
from django.db.models.fields import NullBooleanField

# Create your models here.

from players.models import Player

class TeamCategories(models.Model):
    title = models.CharField(max_length=25)
class Team(models.Model):
    TeamName = models.CharField(max_length=50)
    TeamAbout = models.TextField(max_length=300, null=True, blank=True)
    TeamTypte = models.ManyToManyField(TeamCategories)

class TeamPlayers(models.Model):
    Team = models.ForeignKey(Team, on_delete=CASCADE)
    player = models.ForeignKey(Player, on_delete=CASCADE)