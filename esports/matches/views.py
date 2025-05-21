from typing import Match
from django.db import models
from django.shortcuts import render
from django.core.exceptions import PermissionDenied # Added
from . import models
from django.db.models import F,Q

def data_table(request, slug):
    if not request.tenant:
        raise PermissionDenied("Tenant context is required for this view.")

    group_slug = request.GET.get('data')
    
    # Determine context: Tournament, MatchRound, or MatchGroup
    # The original code used the emptiness of a RegisteredTeams query to decide.
    # This is being refactored to check the slug against Tournament, then MatchRound.
    
    is_tournament_level = False
    is_round_level = False
    tournament_obj_for_title = None # To store the fetched tournament object

    try:
        tournament_obj_for_title = models.Tournament.objects.get(slug=slug, tenant=request.tenant)
        is_tournament_level = True
    except models.Tournament.DoesNotExist:
        try:
            # Not a tournament slug, try MatchRound
            round_obj_for_title = models.MatchRound.objects.get(slug=slug, Tournament__tenant=request.tenant)
            is_round_level = True
        except models.MatchRound.DoesNotExist:
            # Not a tournament or round slug. The original code would proceed assuming 'slug' might relate to groups if group_slug is None.
            # This part is complex in original. If 'slug' is not a Tourn. or Round, and group_slug is also None,
            # the original logic would effectively try to show all teams in a round (which is not found).
            # For now, if neither Tournament nor Round is found by 'slug', we let it proceed,
            # and subsequent .get() calls for title might fail if not handled.
            pass

    group_table_data = None
    single_match_related_info_main = None
    
    # This section provides round-level or group-level match information
    if not is_tournament_level: # Original: if not Tournament (RegisteredTeams queryset was empty)
        # 'slug' is likely a MatchRound slug here.
        group_table_data = models.MatchGroup.objects.filter(Round__slug=slug, Round__Tournament__tenant=request.tenant)
        
        if group_slug is not None: # 'slug' is Round, 'group_slug' is Group
            match_table_data_filter = Q(Match__Match_Group__slug=group_slug, Match__Match_Group__Round__Tournament__tenant=request.tenant)
            match_table_data = models.RegisteredTeams.objects.filter(match_table_data_filter)
            table_title = models.MatchGroup.objects.get(slug=group_slug, Round__Tournament__tenant=request.tenant).Group_title
            unique_team_for_match_filter = Q(Match__Match_Group__slug=group_slug, Match__Match_Group__Round__Tournament__tenant=request.tenant)
            unique_team_for_match = models.PlayersPointTable.objects.filter(unique_team_for_match_filter)
            # Context for kill points (used later in loops)
            kill_point_context_filter = Q(Match__Match_Group__Round__slug=slug, Match__Match_Group__Round__Tournament__tenant=request.tenant)
        else: # 'slug' is Round, no specific group selected
            match_table_data_filter = Q(Match__Match_Round__slug=slug, Match__Match_Round__Tournament__tenant=request.tenant)
            match_table_data = models.RegisteredTeams.objects.filter(match_table_data_filter)
            table_title = models.MatchRound.objects.get(slug=slug, Tournament__tenant=request.tenant).Round_title
            unique_team_for_match_filter = Q(Match__Match_Round__slug=slug, Match__Match_Round__Tournament__tenant=request.tenant)
            unique_team_for_match = models.PlayersPointTable.objects.filter(unique_team_for_match_filter)
            # Context for kill points
            kill_point_context_filter = Q(Match__Match_Round__slug=slug, Match__Match_Round__Tournament__tenant=request.tenant)
            
        # Refactoring the implementation for single_match_related_info_main
        # This part is complex and seems to rebuild data structures.
        # We need to ensure that any DB queries within these loops are tenant-aware if they occur.
        # However, 'unique_team_for_match' is already tenant-filtered.
        # The loops are processing this filtered data.
        if unique_team_for_match.exists(): # Check if there's any data to process
            single_match_related_info_main = []
            processed_matches_for_view = {} # Helper to build the nested structure

            for point_entry in unique_team_for_match: # point_entry is a PlayersPointTable instance
                match_slug = point_entry.Match.slug
                
                if match_slug not in processed_matches_for_view:
                    processed_matches_for_view[match_slug] = {
                        "match_info": [
                            point_entry.Match.slug, 
                            point_entry.Match.Match_Title, 
                            point_entry.Match.image, 
                            point_entry.Match.MatchAbout, 
                            point_entry.Match.TimeDate
                        ],
                        "teams": {}
                    }

                current_match_view_data = processed_matches_for_view[match_slug]
                team_slug_in_point_entry = point_entry.teamName.Team.slug # teamName is RegisteredTeam

                if team_slug_in_point_entry not in current_match_view_data["teams"]:
                    current_match_view_data["teams"][team_slug_in_point_entry] = {
                        "team_info": [
                            team_slug_in_point_entry,
                            point_entry.teamName.Team.TeamName
                        ],
                        "players": [] # List of [name, kill_point, slug]
                    }
                
                # Add player data
                player_view_data = [
                    point_entry.player.player.in_game_name, # player is TeamPlayers, player.player is Player
                    point_entry.kill_Point,
                    point_entry.player.player.slug
                ]
                # Avoid duplicate player entries if data model allows multiple point entries per player per match (e.g. different point types)
                # For now, assuming one summary entry as per original structure.
                current_match_view_data["teams"][team_slug_in_point_entry]["players"].append(player_view_data)

            # Convert the processed_matches_for_view dict into the list structure expected by the template
            temp_sub_list = []
            for match_data_dict in processed_matches_for_view.values():
                match_level_list = match_data_dict["match_info"][:] # Copy basic match info
                teams_level_list = []
                for team_data_dict in match_data_dict["teams"].values():
                    team_level_list = team_data_dict["team_info"][:] # Copy basic team info
                    team_level_list.append(team_data_dict["players"]) # Add players list
                    teams_level_list.append(team_level_list)
                match_level_list.append(teams_level_list)
                temp_sub_list.append(match_level_list)
            single_match_related_info_main.append(temp_sub_list) # Original had nested list: main_list -> sub_list -> match_data
            
            

        #for datatable info. This part provides team summaries for the group/round.
        # 'match_table_data' is already tenant-filtered.
        unique_team = {}
        for u_reg_team_entry in match_table_data: # u_reg_team_entry is a RegisteredTeams instance
            team_slug = u_reg_team_entry.Team.slug
            if team_slug not in unique_team:
                info = []
                info.append(u_reg_team_entry.Team.Team_image.url if u_reg_team_entry.Team.Team_image else None)
                info.append(u_reg_team_entry.Team.TeamName)
                
                # All sub-queries here must use the 'match_table_data_filter' for context and tenant awareness
                win_count = models.RegisteredTeams.objects.filter(match_table_data_filter & Q(Team__slug=team_slug) & Q(Win=True)).count()
                play_count = models.RegisteredTeams.objects.filter(match_table_data_filter & Q(Team__slug=team_slug)).count()
                placement_point_entries = models.RegisteredTeams.objects.filter(match_table_data_filter & Q(Team__slug=team_slug))
                
                total_pp = sum(entry.Placement_Point for entry in placement_point_entries)
                
                # 'kill_point_context_filter' was defined earlier based on round/group context
                kill_point_entries = models.PlayersPointTable.objects.filter(kill_point_context_filter & Q(teamName__Team__slug=team_slug))
                total_kill_point = sum(kp_entry.kill_Point for kp_entry in kill_point_entries)
                total_point = total_kill_point + total_pp
                
                info.append(play_count)
                info.append(win_count)
                info.append(total_pp)
                info.append(total_kill_point) 
                info.append(total_point)
                unique_team[team_slug] = info
    else: # This is tournament_level (is_tournament_level = True)
        match_table_data_filter = Q(Match__Match_Tournament__slug=slug, Match__Match_Tournament__tenant=request.tenant)
        match_table_data = models.RegisteredTeams.objects.filter(match_table_data_filter)
        table_title = tournament_obj_for_title.Tournament_title # Use the fetched tournament

        unique_team = {}
        for u_reg_team_entry in match_table_data: # u_reg_team_entry is RegisteredTeams
            team_slug = u_reg_team_entry.Team.slug
            if team_slug not in unique_team:
                info = []
                info.append(u_reg_team_entry.Team.Team_image.url if u_reg_team_entry.Team.Team_image else None)
                info.append(u_reg_team_entry.Team.TeamName)
                
                win_count = models.RegisteredTeams.objects.filter(match_table_data_filter & Q(Team__slug=team_slug) & Q(Win=True)).count()
                play_count = models.RegisteredTeams.objects.filter(match_table_data_filter & Q(Team__slug=team_slug)).count()
                placement_point_entries = models.RegisteredTeams.objects.filter(match_table_data_filter & Q(Team__slug=team_slug))
                
                total_pp = sum(entry.Placement_Point for entry in placement_point_entries)
                
                # For tournament level, kill points context is the tournament itself
                kill_point_entries = models.PlayersPointTable.objects.filter(Q(Match__Match_Tournament__slug=slug, Match__Match_Tournament__tenant=request.tenant) & Q(teamName__Team__slug=team_slug))
                total_kill_point = sum(kp_entry.kill_Point for kp_entry in kill_point_entries)
                total_point = total_kill_point + total_pp
                
                info.append(play_count)
                info.append(win_count)
                info.append(total_pp)
                info.append(total_kill_point) 
                info.append(total_point)
                unique_team[team_slug] = info
    
    #final sorting
    # Ensure unique_team has items and they have enough elements for sorting key (index 6 is total_point)
    if unique_team and all(len(val_list) >= 7 for val_list in unique_team.values()):
        unique_team_sorted = sorted(unique_team.items(), key=lambda x: x[1][6], reverse=True)
    else:
        unique_team_sorted = [] # Handle empty or malformed data

    context = {
        "table_title": table_title,
        "unique_team" :unique_team_sorted,
        "group_table_data":group_table_data, 
        "single_match_related_info":single_match_related_info_main,
        }

    return render(request, 'matches/matches.html', context)


def upCommingMatches(request):
    # This view is not specified to be tenant-aware.
    # If it were, it would need:
    # if not request.tenant: raise PermissionDenied("Tenant context required.")
    # And queries like models.Match.objects.filter(Match_Tournament__tenant=request.tenant, ...)
    return render(request, 'matches/upcomingmatch.html', {})

def rankList(request, slug):
    if not request.tenant:
        raise PermissionDenied("Tenant context is required for this view.")

    # Corrected rank_data query with tenant filter
    rank_data_filter = Q(Match__Match_Tournament__slug=slug) & \
                       Q(Match__Match_Tournament__tenant=request.tenant) & \
                       Q(Match__Match_Tournament__mvp_expected=True) & \
                       Q(Match__Use_for_Ranking=True)
    rank_data = models.PlayersPointTable.objects.filter(rank_data_filter)
    
    match_list = []
    for i in rank_data: # rank_data is already filtered
        if i.Match.Match_Round.Round_title not in match_list:
            match_list.append(i.Match.Match_Round.Round_title)
    
    # turnamentdetails query with tenant filter
    turnamentdetails_qs = models.PlayersPointTable.objects.filter(
        Match__Match_Tournament__slug=slug,
        Match__Match_Tournament__tenant=request.tenant
    )
    turnament_details_list = [] # Use a new list to avoid context name clash
    # Get unique 'about' text from the related tournament(s)
    # (though 'slug' implies one tournament, the original code structure iterates)
    processed_tournaments_for_about = set()
    for i in turnamentdetails_qs:
        tourn = i.Match.Match_Tournament
        if tourn.slug not in processed_tournaments_for_about:
            if tourn.about:
                 turnament_details_list.append(tourn.about)
            processed_tournaments_for_about.add(tourn.slug)
    
    # mvp_top query, really just to get mvp_count from the Tournament.
    # A more direct query on Tournament model would be better.
    try:
        tournament_for_mvp = models.Tournament.objects.get(
            slug=slug, 
            tenant=request.tenant,
            mvp_expected=True # Assuming this is a condition for having MVP count
        )
        mvp_count = tournament_for_mvp.number_of_mvp
    except models.Tournament.DoesNotExist:
        mvp_count = 0 # Or handle as an error if MVP tournament expected but not found

    players = {}
    # rank_data is already filtered by tenant.
    for p_point_entry in rank_data: # p_point_entry is a PlayersPointTable instance
        player_slug = p_point_entry.player.player.slug # player is TeamPlayer, player.player is Player
        
        if player_slug not in players: # Aggregate points per player
            # Query for all kill points for this player under this specific tournament context
            # This is somewhat redundant if rank_data already contains all necessary entries for summation,
            # but original code did a sub-query. Let's ensure this sub-query is also tenant-aware.
            kill_point_sum_qs = models.PlayersPointTable.objects.filter(
                Match__Match_Tournament__slug=slug,
                Match__Match_Tournament__tenant=request.tenant,
                Match__Match_Tournament__mvp_expected=True, # from rank_data context
                Match__Use_for_Ranking=True, # from rank_data context
                player__player__slug=player_slug
            )
            total_kill_point = sum(entry.kill_Point for entry in kill_point_sum_qs)

            single = [
                player_slug,
                p_point_entry.player.player.in_game_name,
                p_point_entry.player.player.user.photo.url if p_point_entry.player.player.user.photo else None,
                p_point_entry.player.player.age,
                p_point_entry.player.player.nationality,
                p_point_entry.teamName.Team.TeamName, # teamName is RegisteredTeams
                total_kill_point
            ]
            players[player_slug] = single
        # If player_slug is already in players, we assume the first entry encountered had the sum,
        # or that rank_data provides one entry per player for this specific aggregation.
        # If multiple entries for same player in rank_data, this might only take the first.
        # The kill_point_sum_qs above should correctly sum all for that player.

    sorted_players_all = sorted(players.items(), key=lambda x: x[1][6], reverse=True) # Sort by total_kill_point

    sorted_players_top = sorted_players_all[:mvp_count] if mvp_count > 0 else []
    
    context = {
        "turnament_details": turnament_details_list, # Use the new list name
        "match_list":match_list,
        "sorted_players":sorted_players_all,
        "sorted_players_top":sorted_players_top,
    }

    return render(request, 'matches/rank_list.html', context )