from re import T
from django.db import models

# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=200)
    nationality = models.CharField(max_length=200)
    age = models.IntegerField()
    about = models.TextField(max_length=400, null=True, blank=True)
    speciality = models.TextField(max_length=200, null=True, blank=True)
    present_position = models.TextField(max_length=200, null=True, blank=True)
