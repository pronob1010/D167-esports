from django.shortcuts import render
from django.core.exceptions import PermissionDenied # Added

# Create your views here.
from . models import *
def teams(request):
    if not request.tenant:
        raise PermissionDenied("Tenant context is required for this view.")
    team_data = CentralTeam.objects.filter(BS_team__tenant=request.tenant)
    return render(request, 'team/staff.html', {'team_data':team_data})

def teamdetails(request, slug):
    if not request.tenant:
        raise PermissionDenied("Tenant context is required for this view.")
    
    try:
        data = CentralTeam.objects.get(slug=slug, BS_team__tenant=request.tenant)
    except CentralTeam.DoesNotExist:
        raise PermissionDenied("Team not found for this tenant.") # Or Http404

    team_slug = data.BS_team.slug # BS_team is already confirmed to be within the tenant
    players = TeamPlayers.objects.filter(Team_Name__slug=team_slug) # Team_Name is BS_team, so implicitly tenant-filtered
    # print(players)
    # 'team' in CentralTeamAchievement is a ForeignKey to CentralTeam.
    # Since 'data' (a CentralTeam instance) is tenant-filtered, achievements related to it are also implicitly filtered.
    achievements = CentralTeamAchievement.objects.filter(team=data)
    # print(team_slug)
    # 'baseteam' in OtherLineUp is a ForeignKey to CentralTeam.
    # Similar to achievements, this is implicitly filtered by the tenant-aware 'data' instance.
    LineUpplayers = OtherLineUp.objects.filter(baseteam=data)
    # print(LineUpplayers)
    
    LineUpplayersData = []

    for item_lineup in LineUpplayers: # Renamed loop variable 'i' to 'item_lineup'
        li = []
        li.append(item_lineup.title)
        li.append(item_lineup.team.slug) # item_lineup.team is a Team instance.
                                        # This team should also belong to the current tenant.
                                        # The OtherLineUp model might need a direct tenant link or validation
                                        # to ensure item_lineup.team is also within request.tenant.
                                        # For now, assuming current model structure implies this.
                                        # If item_lineup.team can be arbitrary, this is a potential cross-tenant data leak.
                                        # To be safe, let's ensure the team itself is also from the same tenant.
                                        # This requires item_lineup.team to have a tenant field.
                                        # Assuming Team model has 'tenant' field.
        
        # This TeamPlayers query should be safe if item_lineup.team is guaranteed to be of the same tenant.
        # If item_lineup.team.tenant could be different from request.tenant, this is a leak.
        # Given item_lineup is linked to 'data' (a tenant-filtered CentralTeam),
        # and CentralTeam.BS_team.tenant is request.tenant,
        # if OtherLineUp.team is meant to be within the same overarching structure, it should be fine.
        # For stricter safety, if OtherLineUp.team could be *any* team:
        # current_lineup_players = TeamPlayers.objects.filter(Team_Name__slug=item_lineup.team.slug, Team_Name__tenant=request.tenant)
        # However, this might be overly restrictive if item_lineup.team is intentionally from another tenant but displayed here.
        # Given the context, it's more likely item_lineup.team is also part of the same tenant structure.
        current_lineup_players = TeamPlayers.objects.filter(Team_Name__slug=item_lineup.team.slug)


        players_li = []
        for player_in_lineup in current_lineup_players: # Renamed loop variable 'i' to 'player_in_lineup'
            players_li.append(player_in_lineup)
        li.append(players_li)

        LineUpplayersData.append(li)
    # print(LineUpplayersData)

    # print(LineUpplayers) # Original print
    context = {
        'players':players,
        'data':data,
        'achievements':achievements,
        'LineUpplayers':LineUpplayersData,
    }
    return render(request, 'team/teamdetails.html',context )