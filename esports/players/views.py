from django.shortcuts import render
from.models import *
from matches . models import PlayersPointTable
# Create your views here.
def player(request, slug):
    player = Player.objects.get(slug = slug)

    personal_match_data = PlayersPointTable.objects.filter(player__player__slug = slug)
    # for i in personal_match_data:
    #     print(i.kill_Point)

    context = {
        "player": player,
        "personal_match_data":personal_match_data,
    }
    return render(request, 'player/player.html', context)