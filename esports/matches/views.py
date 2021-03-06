from typing import Match
from django.db import models
from django.shortcuts import render

from . import models
from django.db.models import F,Q

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
            #     print(i.Match.Match_Title,"|", iTeamName, "|", i.player.player.in_game_name,"|", i.kill_Point )
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
                                    if k.player.player.in_game_name not in player_data_sub2:
                                        if j.teamName.Team.slug == k.teamName.Team.slug:
                                            player_data_sub2.append(k.player.player.in_game_name)
                                            player_data_sub2.append(k.kill_Point)
                                            player_data_sub2.append(k.player.player.slug)
                                            

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


def upCommingMatches(request):
    return render(request, 'matches/upcomingmatch.html', {})

def rankList(request, slug):
    rank_data = models.PlayersPointTable.objects.filter(Q(Match__Match_Tournament__slug= slug) and Q(Match__Match_Tournament__mvp_expected = True) and Q(Match__Use_for_Ranking = True))
    match_list = []
    for i in rank_data:
        if i.Match.Match_Round.Round_title not in match_list:
            match_list.append(i.Match.Match_Round.Round_title)
    
    turnamentdetails  =  models.PlayersPointTable.objects.filter(Match__Match_Tournament__slug= slug)
    turnament_details = []
    for i in turnamentdetails:
        turnament_details.append(i.Match.Match_Tournament.about)
    

    mvp_top = models.PlayersPointTable.objects.filter(Match__Match_Tournament__slug= slug)
    mvp_count = 0
    for m in mvp_top:
        mvp_count = m.Match.Match_Tournament.number_of_mvp

    players = {}
    for p in rank_data:
        single = []
        single.append(p.player.player.slug)
        single.append(p.player.player.in_game_name)
        single.append(p.player.player.user.photo)
        single.append(p.player.player.age)
        single.append(p.player.player.nationality)
        single.append(p.teamName.Team.TeamName)
        
        kill_point = models.PlayersPointTable.objects.filter(Q(Match__Match_Tournament__slug= slug) and Q(Match__Match_Tournament__mvp_expected = True) and Q(Match__Use_for_Ranking = True) and Q(player__player__slug = p.player.player.slug ))
        kills = []
        for k in kill_point:
            kills.append(k.kill_Point)
        total_kill_point = sum(kills)

        single.append(total_kill_point)
        
        players[p.player.player.slug] = single

    sorted_players_all = sorted(players.items(), key = lambda x:(x[1][6]), reverse=True)
    # for i in sorted_players:
    #     print(i[0],i[1][5])

    sorted_players_top = sorted_players_all[:mvp_count]
    print(sorted_players_top)
    context = {
        "turnament_details":turnament_details,
        "match_list":match_list,
        "sorted_players":sorted_players_all,
        "sorted_players_top":sorted_players_top,
    }

    return render(request, 'matches/rank_list.html', context )