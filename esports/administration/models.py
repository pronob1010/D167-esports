from django.db import models
from django.db.models.deletion import CASCADE

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
    site = models.OneToOneField(SiteInfo, on_delete=CASCADE)
    title = models.CharField(max_length=20)
    link = models.URLField()
