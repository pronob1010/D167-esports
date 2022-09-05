from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.expressions import Case
from django.template.defaultfilters import default, slugify, title
class SiteInfo(models.Model):
    title = models.CharField(max_length=15)
    primary_logo = models.ImageField(upload_to='basic')
    favicon = models.ImageField(upload_to='basic', null=True, blank=True)
    main_cover_image = models.ImageField(upload_to="basic", null=True, blank="True")
    official_mail = models.EmailField(null=True, blank=True)
    help_line = models.CharField(max_length=20,null=True, blank=True)
    physical_address = models.CharField(max_length=100)
    on_google_map = models.URLField(null=True, blank=True)

class SiteAbout(models.Model):
    site = models.OneToOneField(SiteInfo, on_delete=CASCADE, null=True, blank=True)
    banner = models.ImageField(upload_to='basic', default="../static/images/common/esport-team-landing-news-big.jpg", null= True, blank =True)
    about_us = models.TextField(max_length=1000, null=True, blank = True)

class Top_achivment(models.Model):
    site = models.ForeignKey(SiteInfo, on_delete=CASCADE, null=True, blank=True)
    single_line_achivment = models.CharField(max_length=30)

class sponsor_details(models.Model):
    site = models.ForeignKey(SiteInfo, on_delete=CASCADE, null=True, blank=True)
    title = models.CharField(max_length=30, null=True, blank= True)
    about = models.TextField(max_length=150, null=True, blank=True)
    logo = models.ImageField(upload_to='sponsor', null= True, blank =True)

class SocialMediaLinks(models.Model):
    site = models.OneToOneField(SiteInfo, on_delete=CASCADE, null=True, blank=True)
    discord = models.URLField(null=True, blank=True)
    twitch = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)

class broadcast(models.Model):
    title = models.CharField(max_length=50)
    link = models.URLField()
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class LegendZone(models.Model):
    Caption = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to="basic", null=True, blank = True)
    base_story = models.TextField(max_length=500, null=True, blank=True)

    person_1 = models.CharField(max_length=25)
    story_of_person_1 = models.TextField(max_length=250)

    person_2 = models.CharField(max_length=25)
    story_of_person_2 = models.TextField(max_length=250)


class SubAdminCategories(models.Model):
    title = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


from Accounts. models import User
class SubAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True)
    categories = models.ForeignKey(SubAdminCategories, on_delete=CASCADE, null=True, blank=True)
    def __str__(self):
        return self.user.username


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_sub_admin(sender, instance, created, **kwargs):
    if SubAdmin.objects.filter(user=instance).exists() == False:
        if created == False and instance.sub_admin == True:
            SubAdmin.objects.create(user=instance)

# post_save.connect()


class TournamentHost(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True)
    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_host(sender, instance, created, **kwargs):
    if TournamentHost.objects.filter(user=instance).exists() == False:
        if created == False and instance.host == True:
            TournamentHost.objects.create(user = instance)