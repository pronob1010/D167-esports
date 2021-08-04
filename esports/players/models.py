from functools import update_wrapper
from re import T
from typing import DefaultDict
from django.db import models

# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to="players", default='../static/Soldier.png', null=True, blank= True)
    nationality = models.CharField(max_length=200)
    age = models.IntegerField()
    about = models.TextField(max_length=400, null=True, blank=True)
    speciality = models.CharField(max_length=200, null=True, blank=True)
    present_position = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name