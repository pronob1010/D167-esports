from django.contrib import admin

from . models import *


class custom_admin2(admin.StackedInline):
    model = SiteAbout

class custom_admin3(admin.StackedInline):
    model = Top_achivment

class custom_admin4(admin.StackedInline):
    model = sponsor_details

class custom_admin5(admin.StackedInline):
    model = SocialMediaLinks


class custom_admin(admin.ModelAdmin):
    inlines = [custom_admin2, custom_admin3, custom_admin4, custom_admin5]

admin.site.register(SiteInfo, custom_admin)
admin.site.register(LegendZone)
admin.site.register(broadcast) 
admin.site.register(SubAdminCategories)
admin.site.register(SubAdmin)
admin.site.register(TournamentHost)