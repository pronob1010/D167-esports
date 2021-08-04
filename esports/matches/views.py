from django.db import models
from django.shortcuts import render

from . models import *
from django.db.models import F,Q
def matches(request):
    season = request.GET.get('season')
    if season is None:
        season = SEASON.objects.get(pk=1).slug
    
    season_table_data_1 = SEASON.objects.all()[:1]
    season_table_data = SEASON.objects.all()[1:]

    match_table_data = RegisteredTeams.objects.filter(Match__Match_SEASON__slug = season)
    unique_team = {}
    
    i = 0
    j = 0 
    for u in match_table_data:
        info = []
        if u.Team.slug not in info:
            j+=1
            slug = u.Team.slug
            info.append(u.Team.Team_image.url)
            info.append(u.Team.TeamName)
            
            
            win_count = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
            play_count = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(Team__slug = u.Team.slug)).count()
            placement_point = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(Team__slug = u.Team.slug))


            pp = []
            for i in placement_point:
                pp.append(i.Placement_Point)
            total_pp = sum(pp)
            
            kill_point = PlayersPointTable.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(teamName__Team__slug = u.Team.slug))
            kills = []
            for k in kill_point:
                kills.append(k.kill_Point)
            total_kill_point = sum(kills)
            total_point = total_kill_point + total_pp
            # print(win_count,play_count,total_pp,total_kill_point,total_point)
            info.append(play_count)
            info.append(win_count)
            info.append(total_pp)
            info.append(total_kill_point) 
            info.append(total_point)
            print(info)

        unique_team[slug] = info

    print(unique_team)
    
    # match_table_data = RegisteredTeams.objects.all()
    

    context = {
        
        "unique_team" :unique_team,
        "match_table_data":match_table_data, 
        "season_table_data_1":season_table_data_1,
        "season_table_data":season_table_data,
        }
    return render(request, 'matches/matches.html', context)

def liveMatches(request):
    return render(request, 'matches/matchlive.html', {})

def upCommingMatches(request):
    return render(request, 'matches/upcomingmatch.html', {})