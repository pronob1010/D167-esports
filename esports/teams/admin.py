
from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(TeamCategories)

class TeamPlayersAdmin(admin.TabularInline):
    model = TeamPlayers

class TeamAdmin(admin.ModelAdmin):
    inlines = [TeamPlayersAdmin]

admin.site.register(Team, TeamAdmin)