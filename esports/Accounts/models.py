from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case
from django.db.models.fields import TextField
from . manager import UserManager

class BaseUser(models.Model):
    photo = models.ImageField(upload_to="user", default='../static/Soldier.png', null=True, blank= True)
    nationality = models.CharField(max_length=200, null=True, blank= True)
    age = models.IntegerField(null=True, blank= True)
    about = models.TextField(max_length=150, null=True, blank=True)
    
    class Meta:
        abstract = True


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=30, unique=True)
    sub_admin = models.BooleanField(default=False)
    player = models.BooleanField(default=False)

    forget_password = models.CharField(max_length=100, null=True, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_logout_time = models.DateTimeField(null=True, blank=True)
    is_varified = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'phone'  
    # REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

class UserProfile(BaseUser):
    user = models.OneToOneField(User, on_delete=CASCADE)
    date_of_join = models.DateTimeField(auto_now_add=True)


class UserSocialMedia(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True)
    discord = models.URLField(null=True, blank=True)
    twitch = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)

class shareMediaOrText(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True)
    text = models.TextField(max_length=150, null=True, blank = True)
    link = models.URLField(null=True, blank=True)