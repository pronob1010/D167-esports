from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case
from django.db.models.fields import NullBooleanField

# Create your models here.

from players.models import Player

class Team_Categories(models.Model):
    title = models.CharField(max_length=25)
class Team(models.Model):
    Team_Name = models.CharField(max_length=50)
    Team_About = models.TextField(max_length=300, null=True, blank=True)
    Team_Typte = models.ManyToManyField(Team_Categories,null=True, blank=True)

class Team_Players(models.Model):
    Team = models.ForeignKey(Team, on_delete=CASCADE)
    player = models.ForeignKey(Player, on_delete=CASCADE)