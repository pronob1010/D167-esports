from django.db import models
from django.shortcuts import render

from . models import *
from django.db.models import F,Q
# def matches(request):
#     match_data = MatchGroup.objects.all()
#     unique_season = []
#     for s in match_data:
#         li = []
#         if s.Season.slug not in li:
#             li.append(s.Season.slug)
#             li.append(s.Season.SEASON_title)

#             round= MatchRound.objects.filter(Season__slug=s.Season.slug)
#             rounds = {}
#             for r in round:
#                 if r.slug not in rounds:
#                     rounds[r.slug]=r.Round_title
#             li.append(rounds)
#         if li not in unique_season:
#             unique_season.append(li)

#     # print(unique_season)

#     season = request.GET.get('season_slug')
#     print(season)
#     # if season is None:
#     #     season = SEASON.objects.get(pk=1).slug
    
#     # season_table_data_1 = SEASON.objects.all()[:1]
#     # season_table_data = SEASON.objects.all()[1:]

#     # match_table_data = RegisteredTeams.objects.filter(Match__Match_SEASON__slug = season)
#     # unique_team = {}
    
#     # i = 0
#     # j = 0 
#     # for u in match_table_data:
#     #     info = []
#     #     if u.Team.slug not in info:
#     #         j+=1
#     #         slug = u.Team.slug
#     #         info.append(u.Team.Team_image.url)
#     #         info.append(u.Team.TeamName)
            
            
#     #         win_count = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
#     #         play_count = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(Team__slug = u.Team.slug)).count()
#     #         placement_point = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(Team__slug = u.Team.slug))


#     #         pp = []
#     #         for i in placement_point:
#     #             pp.append(i.Placement_Point)
#     #         total_pp = sum(pp)
            
#     #         kill_point = PlayersPointTable.objects.filter(Q(Match__Match_SEASON__slug = season) & Q(teamName__Team__slug = u.Team.slug))
#     #         kills = []
#     #         for k in kill_point:
#     #             kills.append(k.kill_Point)
#     #         total_kill_point = sum(kills)
#     #         total_point = total_kill_point + total_pp
#     #         # print(win_count,play_count,total_pp,total_kill_point,total_point)
#     #         info.append(play_count)
#     #         info.append(win_count)
#     #         info.append(total_pp)
#     #         info.append(total_kill_point) 
#     #         info.append(total_point)
#     #         # print(info)

#     #     unique_team[slug] = info

#     # print(unique_team)
    
#     # # match_table_data = RegisteredTeams.objects.all()
    

#     context = {
        
#         # "unique_team" :unique_team,
#         # "match_table_data":match_table_data, 
#         # "season_table_data_1":season_table_data_1,
#         # "season_table_data":season_table_data,

#         "nav_season":unique_season,
#         }
#     return render(request, 'matches/matches.html', context)
#     # return render(request, 'matches/matches.html', {})


def data_table(request, slug):
    group_slug = request.GET.get('data')
    season = RegisteredTeams.objects.filter(Match__Match_SEASON__slug = slug)    
    # group_table_data = MatchGroup.objects.filter(Season__slug = slug)
    group_table_data = None
    
    #This section provide round level match information
    if not season:
        group_table_data = MatchGroup.objects.filter(Round__slug = slug)
        if group_slug is not None:
            match_table_data = RegisteredTeams.objects.filter(Match__Match_Group__slug = group_slug)
            print(match_table_data)
            table_title = MatchGroup.objects.get(slug = group_slug).Group_title

            unique_team = {}
            j = 0 
            for u in match_table_data:
                info = []
                if u.Team.slug not in info:
                    j+=1
                    team_slug = u.Team.slug
                    info.append(u.Team.Team_image.url)
                    info.append(u.Team.TeamName)
                    
                    
                    win_count = RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) &Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
                    play_count = RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) & Q(Team__slug = u.Team.slug)).count()
                    print(RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) & Q(Team__slug = u.Team.slug)).count())
                    placement_point = RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) & Q(Team__slug = u.Team.slug))


                    pp = []
                    for i in placement_point:
                        pp.append(i.Placement_Point)
                    total_pp = sum(pp)
                    
                    kill_point = PlayersPointTable.objects.filter(Q(Match__Match_Round__slug = slug) & Q(teamName__Team__slug = u.Team.slug))
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
                    # print(info)

                unique_team[team_slug] = info
            
        else:
            match_table_data = RegisteredTeams.objects.filter(Match__Match_Round__slug = slug)
        # print(match_table_data)
            table_title = MatchRound.objects.get(slug = slug).Round_title

            unique_team = {}
            j = 0 
            for u in match_table_data:
                info = []
                if u.Team.slug not in info:
                    j+=1
                    team_slug = u.Team.slug
                    info.append(u.Team.Team_image.url)
                    info.append(u.Team.TeamName)
                    
                    
                    win_count = RegisteredTeams.objects.filter(Q(Match__Match_Round__slug = slug) &Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
                    play_count = RegisteredTeams.objects.filter(Q(Match__Match_Round__slug = slug) & Q(Team__slug = u.Team.slug)).count()
                    placement_point = RegisteredTeams.objects.filter(Q(Match__Match_Round__slug = slug) & Q(Team__slug = u.Team.slug))


                    pp = []
                    for i in placement_point:
                        pp.append(i.Placement_Point)
                    total_pp = sum(pp)
                    
                    kill_point = PlayersPointTable.objects.filter(Q(Match__Match_Round__slug = slug) & Q(teamName__Team__slug = u.Team.slug))
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
                    # print(info)

                unique_team[team_slug] = info

            # print(unique_team)
            
        #This section provide season level match information
    else:
        match_table_data = RegisteredTeams.objects.filter(Match__Match_SEASON__slug = slug)
        table_title = SEASON.objects.get(slug = slug).SEASON_title
        
        unique_team = {}
        j = 0 
        for u in match_table_data:
            info = []
            if u.Team.slug not in info:
                j+=1
                team_slug = u.Team.slug
                info.append(u.Team.Team_image.url)
                info.append(u.Team.TeamName)
                
                
                win_count = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = slug) & Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
                play_count = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = slug) & Q(Team__slug = u.Team.slug)).count()
                placement_point = RegisteredTeams.objects.filter(Q(Match__Match_SEASON__slug = slug) & Q(Team__slug = u.Team.slug))


                pp = []
                for i in placement_point:
                    pp.append(i.Placement_Point)
                total_pp = sum(pp)
                
                kill_point = PlayersPointTable.objects.filter(Q(Match__Match_SEASON__slug = slug) & Q(teamName__Team__slug = u.Team.slug))
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
                # print(info)

            unique_team[team_slug] = info

        # print(unique_team)
    # print(unique_team)
    
    #final sorting
    unique_team = sorted(unique_team.items(), key = lambda x:(x[1][6]), reverse=True)
    # for i in unique_team_new:
    #     print(i[0],i[1][1])

    context = {
        "table_title": table_title,
        "unique_team" :unique_team,
        "group_table_data":group_table_data, 
        }

    return render(request, 'matches/matches.html', context)

def liveMatches(request):
    return render(request, 'matches/matchlive.html', {})

def upCommingMatches(request):
    return render(request, 'matches/upcomingmatch.html', {})