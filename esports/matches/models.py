from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import related
from teams.models import Team

class Matche_Categories(models.Model):
    title = models.CharField(max_length=25)

class Matche_Level(models.Model):
    title = models.CharField(max_length=25)

class Matche(models.Model):
    Team_1 = models.ForeignKey(Team, on_delete=CASCADE, related_name="Team1")
    Team_2 = models.ForeignKey(Team, on_delete=CASCADE, related_name="Team2")
    Match_Category = models.ForeignKey(Matche_Categories, on_delete=CASCADE, related_name="category")
    Match_Level = models.ForeignKey(Matche_Level, on_delete=CASCADE,  related_name="level")
    Featured = models.BooleanField(default=False)
    Score_of_Team_1 = models.IntegerField(default=0)
    Score_of_Team_2 = models.IntegerField(default=0)
