from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from .models import PlayersPointTable, Match, RegisteredTeams
from players.models import Player
from teams.models import TeamPlayers # To access Player from TeamPlayers

@receiver(post_save, sender=PlayersPointTable)
def update_player_stats_from_point_table(sender, instance, created, **kwargs):
    """
    Updates total_kills for a player when a new PlayersPointTable entry is created.
    """
    if created:
        try:
            # instance.player is a GroupedForeignKey to TeamPlayers
            # TeamPlayers has a foreign key 'player' to the Player model.
            if instance.player and hasattr(instance.player, 'player') and instance.player.player:
                player_obj = instance.player.player # This is the actual Player instance
                
                # Increment total_kills
                player_obj.total_kills = F('total_kills') + instance.kill_Point
                player_obj.save(update_fields=['total_kills'])
                player_obj.refresh_from_db() # Ensure the local object has the updated value for any subsequent operations
            else:
                # This case might happen if instance.player or instance.player.player is None
                # Or if the structure is different than expected.
                # print(f"Could not find Player object for PlayersPointTable: {instance.id}")
                pass
        except Player.DoesNotExist:
            # print(f"Player DoesNotExist for PlayersPointTable: {instance.id}, TeamPlayer: {instance.player_id}")
            pass # Handle cases where the player might not exist, though FK constraints should prevent this.
        except Exception as e:
            # print(f"Error in update_player_stats_from_point_table: {e}")
            pass # Catch any other potential errors

@receiver(post_save, sender=Match)
def update_player_stats_on_match_completion(sender, instance, created, **kwargs):
    """
    Updates total_matches_played for players when a Match's Use_for_Ranking becomes True.
    MVP awards logic is conceptual here and would require a defined way to determine MVP.
    """
    # Check if 'Use_for_Ranking' was changed to True
    # This requires knowing the previous state if possible, or just acting if it's True.
    # For simplicity, if Use_for_Ranking is True, we process.
    # To prevent re-counting, a flag on the Match instance (e.g., stats_tallied = BooleanField(default=False))
    # would be ideal. Without it, this signal might run multiple times if a Match is saved multiple times
    # while Use_for_Ranking is True.
    # For now, we'll proceed with the simplified assumption. A more robust solution would track prior state or use a flag.

    if instance.Use_for_Ranking:
        # A flag to prevent reprocessing would be good here, e.g., if not instance.stats_processed:
        try:
            registered_teams_in_match = RegisteredTeams.objects.filter(Match=instance)
            unique_player_ids_in_match = set()

            for reg_team in registered_teams_in_match:
                # reg_team.Team is a Team instance. We need TeamPlayers associated with this Team.
                team_players = TeamPlayers.objects.filter(Team_Name=reg_team.Team)
                for tp_entry in team_players:
                    if tp_entry.player: # tp_entry.player is the Player instance
                        unique_player_ids_in_match.add(tp_entry.player.id)
            
            # Increment total_matches_played for all unique players
            for player_id in unique_player_ids_in_match:
                try:
                    player_obj = Player.objects.get(id=player_id)
                    player_obj.total_matches_played = F('total_matches_played') + 1
                    player_obj.save(update_fields=['total_matches_played'])
                except Player.DoesNotExist:
                    # print(f"Player with id {player_id} not found during match completion stat update.")
                    pass
            
            # MVP Logic (conceptual - would need a clear MVP determination method)
            # if instance.Match_Tournament and instance.Match_Tournament.mvp_expected:
            #     # 1. Determine MVP(s) for 'instance' (the match)
            #     #    This logic could be complex, e.g., highest score from PlayersPointTable for this match.
            #     #    Let's assume a hypothetical function get_mvp_for_match(match_instance) -> Player object or None
            #     mvp_player = get_mvp_for_match(instance) # This function needs to be implemented
            #     if mvp_player:
            #         try:
            #             mvp_player_obj = Player.objects.get(id=mvp_player.id) # Ensure it's a Player model instance
            #             mvp_player_obj.mvp_awards = F('mvp_awards') + 1
            #             mvp_player_obj.save(update_fields=['mvp_awards'])
            #         except Player.DoesNotExist:
            #             pass # MVP player not found in Player table

            # Mark match as processed if a flag field existed (e.g., instance.stats_processed = True; instance.save())

        except Exception as e:
            # print(f"Error in update_player_stats_on_match_completion: {e}")
            pass # Catch any potential errors
