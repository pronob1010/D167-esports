from django.db import models
from django.db.models.deletion import CASCADE
from django.template.defaultfilters import default, slugify


# class Official_Stuff(models.Model):
class SiteInfo(models.Model):
    title = models.CharField(max_length=15)
    primary_logo = models.ImageField(upload_to='basic')
    favicon = models.ImageField(upload_to='basic', null=True, blank=True)
    main_cover_image = models.ImageField(upload_to="basic", null=True, blank="True")
    official_mail = models.EmailField(null=True, blank=True)
    help_line = models.CharField(max_length=20,null=True, blank=True)
    physical_address = models.CharField(max_length=100)

class SocialMediaLinks(models.Model):
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

