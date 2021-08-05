
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(TeamGroup)
class TeamPlayersAdmin(admin.TabularInline):
    model = TeamPlayers

class TeamGroupAdmin(admin.TabularInline):
    model = TeamGroup

class TeamAdmin(admin.ModelAdmin):
    inlines = [TeamPlayersAdmin,]

admin.site.register(Team, TeamAdmin)
