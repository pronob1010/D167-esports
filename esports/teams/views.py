from django.shortcuts import render

# Create your views here.
from . models import *
def teams(request):
    team_data = CentralTeam.objects.all()
    return render(request, 'team/staff.html', {'team_data':team_data})

def teamdetails(request, slug):
    data = CentralTeam.objects.get(slug = slug)
    team_slug = data.BS_team.slug
    players = TeamPlayers.objects.filter(Team_Name__slug = team_slug)
    # print(players)
    achievements = CentralTeamAchievement.objects.filter(team__BS_team__slug = team_slug)
    # print(team_slug)
    LineUpplayers = OtherLineUp.objects.filter(baseteam__BS_team__slug = team_slug)
    # print(LineUpplayers)
    
    LineUpplayersData = []

    for i in LineUpplayers:
        li = []
        li.append(i.title)
        li.append(i.team.slug)
        players = TeamPlayers.objects.filter(Team_Name__slug = i.team.slug)

        players_li = []
        for i in players:
            players_li.append(i)
        li.append(players_li)

        LineUpplayersData.append(li)
    # print(LineUpplayersData)

    # print(LineUpplayers)
    context = {
        'players':players,
        'data':data,
        'achievements':achievements,
        'LineUpplayers':LineUpplayersData,
    }
    return render(request, 'team/teamdetails.html',context )