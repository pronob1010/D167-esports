from typing import DefaultDict
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import F
from Accounts.models import User
from django.template.defaultfilters import slugify
# Create your models here.

from Accounts.models import BaseUser

#to autometicattly create users player profile
from django.db.models.signals import post_save
from django.dispatch import receiver

class Player(BaseUser):
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True, related_name="user_player")
    in_game_name= models.CharField(max_length=200, unique=True, null=True)
    present_position = models.CharField(max_length=200, null=True, blank=True)
    speciality = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            if self.in_game_name is not None:
                self.slug = slugify(self.in_game_name)
            else:
                self.slug = slugify(self.user.username)

        return super().save(*args, **kwargs)

    def __str__(self):
        if self.in_game_name is not None:
            return self.in_game_name
        else:
            return self.user.username 

# @receiver(post_save, sender = User)
# def create_player(sender, instance, created, **kwargs):
#     if User.player is True:
#         Player.objects.create(user = instance)

# @receiver(post_save, sender = User)
# def save_player(sender, instance, **kwargs):
#     instance.user_player.save()

# @receiver(post_save, sender = User)

@receiver(post_save, sender = User)
def create_player(sender, instance, created, **kwargs):
    if Player.objects.filter(user = instance).exists() == False:
        if created == False and instance.player == True:
            Player.objects.create(user = instance)

# post_save.connect(create_player, User)