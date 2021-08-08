from typing import Match
from django.db import models
from django.shortcuts import render

from . import models
from django.db.models import F,Q
# def matches(request):
#     match_data = MatchGroup.objects.all()
#     unique_Tournament = []
#     for s in match_data:
#         li = []
#         if s.Tournament.slug not in li:
#             li.append(s.Tournament.slug)
#             li.append(s.Tournament.Tournament_title)

#             round= MatchRound.objects.filter(Tournament__slug=s.Tournament.slug)
#             rounds = {}
#             for r in round:
#                 if r.slug not in rounds:
#                     rounds[r.slug]=r.Round_title
#             li.append(rounds)
#         if li not in unique_Tournament:
#             unique_Tournament.append(li)

#     # print(unique_Tournament)

#     Tournament = request.GET.get('Tournament_slug')
#     print(Tournament)
#     # if Tournament is None:
#     #     Tournament = Tournament.objects.get(pk=1).slug
    
#     # Tournament_table_data_1 = Tournament.objects.all()[:1]
#     # Tournament_table_data = Tournament.objects.all()[1:]

#     # match_table_data = RegisteredTeams.objects.filter(Match__Match_Tournament__slug = Tournament)
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
            
            
#     #         win_count = RegisteredTeams.objects.filter(Q(Match__Match_Tournament__slug = Tournament) & Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
#     #         play_count = RegisteredTeams.objects.filter(Q(Match__Match_Tournament__slug = Tournament) & Q(Team__slug = u.Team.slug)).count()
#     #         placement_point = RegisteredTeams.objects.filter(Q(Match__Match_Tournament__slug = Tournament) & Q(Team__slug = u.Team.slug))


#     #         pp = []
#     #         for i in placement_point:
#     #             pp.append(i.Placement_Point)
#     #         total_pp = sum(pp)
            
#     #         kill_point = PlayersPointTable.objects.filter(Q(Match__Match_Tournament__slug = Tournament) & Q(teamName__Team__slug = u.Team.slug))
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
#         # "Tournament_table_data_1":Tournament_table_data_1,
#         # "Tournament_table_data":Tournament_table_data,

#         "nav_Tournament":unique_Tournament,
#         }
#     return render(request, 'matches/matches.html', context)
#     # return render(request, 'matches/matches.html', {})


def data_table(request, slug):
    group_slug = request.GET.get('data')
    Tournament = models.RegisteredTeams.objects.filter(Match__Match_Tournament__slug = slug)    
    # group_table_data = MatchGroup.objects.filter(Tournament__slug = slug)
    group_table_data = None
    group_level_all_match = None
    single_match_related_info_main = None
    
    #This section provide round level match information
    if not Tournament:
        group_table_data = models.MatchGroup.objects.filter(Round__slug = slug)
        if group_slug is not None:
            match_table_data = models.RegisteredTeams.objects.filter(Match__Match_Group__slug = group_slug)
            # print(match_table_data)
            table_title = models.MatchGroup.objects.get(slug = group_slug).Group_title
            
            # group_level_all_match = Match.objects.filter(Match_Group__slug = group_slug)
            # print(group_level_all_match)

            #To provide match specific team and players kills details
            unique_team_for_match = models.PlayersPointTable.objects.filter(Match__Match_Group__slug = group_slug)
            
            #match_data_retrive_test
            # for i in unique_team_for_match:
            #     print(i.Match.Match_Title,"|", iTeamName, "|", i.player.player.username,"|", i.kill_Point )
            #     # for j in i.teamName:
            #     #     print(j)
            
            #implementation
            single_match_related_info_main = []
            single_match_related_info_sub=[]
            single_match_related_info_main.append(single_match_related_info_sub)

            for i in unique_team_for_match:
                single_match_related_info_sub2 = []
                if i.Match.slug not in single_match_related_info_sub2:
                    single_match_related_info_sub2.append(i.Match.slug)
                    single_match_related_info_sub2.append(i.Match.Match_Title)
                    single_match_related_info_sub2.append(i.Match.image)
                    single_match_related_info_sub2.append(i.Match.MatchAbout)
                    single_match_related_info_sub2.append(i.Match.TimeDate)


                    team_data_main=[]
                    team_data_sub =[]
                    team_data_main.append(team_data_sub)
                    for j in unique_team_for_match:
                        team_data_sub2 =[]
                        if j.teamName.Team.slug not in team_data_sub2:
                            if i.Match.slug == j.Match.slug:
                                team_data_sub2.append(j.teamName.Team.slug)
                                team_data_sub2.append(j.teamName.Team.TeamName)

                                player_data_main = []
                                player_data_sub = []
                                player_data_main.append(player_data_sub)
                                
                                for k in unique_team_for_match:
                                    player_data_sub2 = []
                                    if k.player.player.username not in player_data_sub2:
                                        if j.teamName.Team.slug == k.teamName.Team.slug:
                                            player_data_sub2.append(k.player.player.username)
                                            player_data_sub2.append(k.kill_Point)

                                    if player_data_sub2 not in player_data_sub:
                                        player_data_sub.append(player_data_sub2)
                                        # print(player_data_sub)
                                team_data_sub2.append(player_data_sub)

                        if team_data_sub2 not in team_data_sub:
                            team_data_sub.append(team_data_sub2)
                            # print(team_data_sub)


                    single_match_related_info_sub2.append(team_data_sub)

                if single_match_related_info_sub2 not in single_match_related_info_sub:
                    single_match_related_info_sub.append(single_match_related_info_sub2)
            
            # single_match_related_info_main.append(single_match_related_info_sub)
            # player_data_main = []
            # player_data_sub = []
            # player_data_main.append(player_data_sub)
            
            # for k in unique_team_for_match:
            #     player_data_sub2 = []
            #     if k.player.player.username not in player_data_sub2:
            #         if unique_team_for_match[2].teamName.Team.slug == k.teamName.Team.slug:
            #             player_data_sub2.append(k.player.player.username)
            #             player_data_sub2.append(k.kill_Point)
            #             print(k.player.player.username, k.kill_Point)
            #     if player_data_sub2 not in player_data_sub:
            #         player_data_sub.append(player_data_sub2)
                
            # print(player_data_sub)


            #for datatable info. This part provide 
            # all teams of an group and related information of teams
            unique_team = {}
            j = 0 
            for u in match_table_data:
                info = []
                if u.Team.slug not in info:
                    j+=1
                    team_slug = u.Team.slug
                    info.append(u.Team.Team_image.url)
                    info.append(u.Team.TeamName)
                    
                    
                    win_count = models.RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) &Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
                    play_count = models.RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) & Q(Team__slug = u.Team.slug)).count()
                    placement_point = models.RegisteredTeams.objects.filter(Q(Match__Match_Group__slug = group_slug) & Q(Team__slug = u.Team.slug))


                    pp = []
                    for i in placement_point:
                        pp.append(i.Placement_Point)
                    total_pp = sum(pp)
                    
                    kill_point = models.PlayersPointTable.objects.filter(Q(Match__Match_Round__slug = slug) & Q(teamName__Team__slug = u.Team.slug))
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
            match_table_data = models.RegisteredTeams.objects.filter(Match__Match_Round__slug = slug)
        # print(match_table_data)
            table_title = models.MatchRound.objects.get(slug = slug).Round_title

            unique_team = {}
            j = 0 
            for u in match_table_data:
                info = []
                if u.Team.slug not in info:
                    j+=1
                    team_slug = u.Team.slug
                    info.append(u.Team.Team_image.url)
                    info.append(u.Team.TeamName)
                    
                    win_count = models.RegisteredTeams.objects.filter(Q(Match__Match_Round__slug = slug) &Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
                    play_count = models.RegisteredTeams.objects.filter(Q(Match__Match_Round__slug = slug) & Q(Team__slug = u.Team.slug)).count()
                    placement_point = models.RegisteredTeams.objects.filter(Q(Match__Match_Round__slug = slug) & Q(Team__slug = u.Team.slug))


                    pp = []
                    for i in placement_point:
                        pp.append(i.Placement_Point)
                    total_pp = sum(pp)
                    
                    kill_point = models.PlayersPointTable.objects.filter(Q(Match__Match_Round__slug = slug) & Q(teamName__Team__slug = u.Team.slug))
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
            
        #This section provide Tournament level match information
    else:
        match_table_data = models.RegisteredTeams.objects.filter(Match__Match_Tournament__slug = slug)
        table_title = models.Tournament.objects.get(slug = slug).Tournament_title
        # print(table)

        unique_team = {}
        j = 0 
        for u in match_table_data:
            info = []
            if u.Team.slug not in info:
                j+=1
                team_slug = u.Team.slug
                info.append(u.Team.Team_image.url)
                info.append(u.Team.TeamName)
                
                
                win_count = models.RegisteredTeams.objects.filter(Q(Match__Match_Tournament__slug = slug) & Q(Team__slug = u.Team.slug) & Q(Win = True)).count()
                play_count = models.RegisteredTeams.objects.filter(Q(Match__Match_Tournament__slug = slug) & Q(Team__slug = u.Team.slug)).count()
                placement_point = models.RegisteredTeams.objects.filter(Q(Match__Match_Tournament__slug = slug) & Q(Team__slug = u.Team.slug))


                pp = []
                for i in placement_point:
                    pp.append(i.Placement_Point)
                total_pp = sum(pp)
                
                kill_point = models.PlayersPointTable.objects.filter(Q(Match__Match_Tournament__slug = slug) & Q(teamName__Team__slug = u.Team.slug))
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
        # "group_level_all_match":group_level_all_match,
        "single_match_related_info":single_match_related_info_main,
        }

    return render(request, 'matches/matches.html', context)

def liveMatches(request):
    return render(request, 'matches/matchlive.html', {})

def upCommingMatches(request):
    return render(request, 'matches/upcomingmatch.html', {})

def rankList(request, slug):
    rank_data = models.PlayersPointTable.objects.filter(Q(Match__Match_Tournament__slug= slug) and Q(Match__Match_Tournament__mvp_expected = True) and Q(Match__Use_for_Ranking = True))
    players = {}
    for p in rank_data:
        single = []
        single.append(p.player.player.slug)
        single.append(p.player.player.username)
        single.append(p.player.player.photo)
        single.append(p.player.player.age)
        single.append(p.player.player.nationality)
        single.append(p.teamName.Team.TeamName)

        
        single.append(p.kill_Point)

        players[p.player.player.slug] = single

    sorted_players = sorted(players.items(), key = lambda x:(x[1][5]), reverse=True)
    # for i in sorted_players:
    #     print(i[0],i[1][5])

    print(sorted_players)
    context = {
        "sorted_players":sorted_players
    }




    return render(request, 'matches/rank_list.html', context )