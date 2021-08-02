from django.contrib import admin

 
from.models import *
class MatchTeamDetailsAdmin(admin.TabularInline):
    model = MatchTeamDetails

class PlayersPointTableAdmin(admin.TabularInline):
    model = PlayersPointTable

class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchTeamDetailsAdmin,PlayersPointTableAdmin]

admin.site.register(Match , MatchAdmin)
admin.site.register(MatchCategories)
admin.site.register(MatchLevel)