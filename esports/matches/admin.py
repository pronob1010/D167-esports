from django.contrib import admin

 
from.models import *
class MatchTeamDetailsAdmin(admin.TabularInline):
    model = RegisteredTeams

class PlayersPointTableAdmin(admin.TabularInline):
    model = PlayersPointTable

class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchTeamDetailsAdmin,PlayersPointTableAdmin]

admin.site.register(Match , MatchAdmin)
admin.site.register(Tournament)
# admin.site.register(Tournament)
admin.site.register(MatchGroup)
admin.site.register(PlayersPointTable)
admin.site.register(MatchRound)
admin.site.register(RegisteredTeams)