from typing import DefaultDict
from django.db import models
from django.db.models.deletion import CASCADE
from Accounts.models import User
from django.template.defaultfilters import slugify
# Create your models here.
class Player(models.Model):
    username = models.CharField(max_length=50,null=True, blank= True)
    photo = models.ImageField(upload_to="players", default='../static/Soldier.png', null=True, blank= True)
    nationality = models.CharField(max_length=200, null=True, blank= True)
    age = models.IntegerField(null=True, blank= True)
    about = models.TextField(max_length=400, null=True, blank=True)
    speciality = models.CharField(max_length=200, null=True, blank=True)
    present_position = models.CharField(max_length=200, null=True, blank=True)

    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.username)
        return super().save(*args, **kwargs)
    def __str__(self):
        return self.username