from django.test import TestCase

from organizers.models import Game
from .models import Match, Tournament, TournamentTeam
from . import services


def make_tournament(n_teams, title="Cup", game=None):
    t = Tournament.objects.create(Tournament_title=title, game=game)
    for i in range(n_teams):
        TournamentTeam.objects.create(tournament=t, name=f"Team {i+1}", seed=i + 1)
    return t


class LeagueFixtureTests(TestCase):
    def test_round_robin_match_count_even(self):
        t = make_tournament(6)
        created = services.generate_league_fixtures(t)
        # n*(n-1)/2 = 15 matches, over n-1 = 5 matchdays.
        self.assertEqual(created, 15)
        self.assertEqual(Match.objects.filter(Match_Tournament=t).count(), 15)
        self.assertEqual(t.rounds.count() if hasattr(t, "rounds") else
                         t.matchround_set.count(), 5)

    def test_round_robin_match_count_odd(self):
        t = make_tournament(5)
        created = services.generate_league_fixtures(t)
        # 5*4/2 = 10 matches, 5 matchdays (one bye each day).
        self.assertEqual(created, 10)

    def test_everyone_plays_everyone_once(self):
        t = make_tournament(4)
        services.generate_league_fixtures(t)
        pairs = set()
        for m in Match.objects.filter(Match_Tournament=t):
            pairs.add(frozenset([m.home_team_id, m.away_team_id]))
        self.assertEqual(len(pairs), 6)  # C(4,2)

    def test_regenerate_is_idempotent(self):
        t = make_tournament(4)
        services.generate_league_fixtures(t)
        services.generate_league_fixtures(t)
        self.assertEqual(Match.objects.filter(Match_Tournament=t).count(), 6)


class StandingsTests(TestCase):
    def test_points_and_ordering(self):
        t = make_tournament(3)
        services.generate_league_fixtures(t)
        teams = {tt.name: tt for tt in t.teams.all()}
        # Team 1 beats 2 and 3; Team 2 beats 3.
        for m in Match.objects.filter(Match_Tournament=t):
            names = {m.home_team.name, m.away_team.name}
            if names == {"Team 1", "Team 2"}:
                self._score(m, "Team 1", 2, 0)
            elif names == {"Team 1", "Team 3"}:
                self._score(m, "Team 1", 1, 0)
            elif names == {"Team 2", "Team 3"}:
                self._score(m, "Team 2", 3, 1)
        rows = services.compute_standings(t)
        self.assertEqual(rows[0]["team"].name, "Team 1")
        self.assertEqual(rows[0]["points"], 6)
        self.assertEqual(rows[1]["team"].name, "Team 2")
        self.assertEqual(rows[1]["points"], 3)
        self.assertEqual(rows[2]["team"].name, "Team 3")
        self.assertEqual(rows[2]["points"], 0)

    def _score(self, match, winner_name, ws, ls):
        if match.home_team.name == winner_name:
            services.record_result(match, ws, ls)
        else:
            services.record_result(match, ls, ws)


class KnockoutFixtureTests(TestCase):
    def test_power_of_two_bracket(self):
        t = make_tournament(8)
        created = services.generate_knockout_fixtures(t)
        # 4 + 2 + 1 = 7 matches.
        self.assertEqual(created, 7)
        # First round fully populated.
        first = Match.objects.filter(
            Match_Tournament=t, Match_Round__Round_title="Quarter-final"
        )
        self.assertEqual(first.count(), 4)
        for m in first:
            self.assertIsNotNone(m.home_team)
            self.assertIsNotNone(m.away_team)

    def test_byes_for_non_power_of_two(self):
        t = make_tournament(6)  # bracket size 8, 2 byes
        services.generate_knockout_fixtures(t)
        first = list(Match.objects.filter(
            Match_Tournament=t, Match_Round__Round_title="Quarter-final"
        ).order_by("order"))
        # Two of the four first-round matches are byes (auto-played).
        byes = [m for m in first if m.is_played]
        self.assertEqual(len(byes), 2)
        # The top two seeds should have advanced via bye into the semi-finals.
        semis = Match.objects.filter(
            Match_Tournament=t, Match_Round__Round_title="Semi-final"
        )
        advanced = [m.home_team for m in semis if m.home_team] + \
                   [m.away_team for m in semis if m.away_team]
        self.assertGreaterEqual(len(advanced), 2)

    def test_winner_advances(self):
        t = make_tournament(4)
        services.generate_knockout_fixtures(t)
        semis = list(Match.objects.filter(
            Match_Tournament=t, Match_Round__Round_title="Semi-final"
        ).order_by("order"))
        self.assertEqual(len(semis), 2)
        w1 = semis[0].home_team
        services.record_result(semis[0], 3, 1)
        w2 = semis[1].away_team
        services.record_result(semis[1], 0, 2)
        final = Match.objects.get(
            Match_Tournament=t, Match_Round__Round_title="Final"
        )
        final.refresh_from_db()
        self.assertEqual(final.home_team_id, w1.id)
        self.assertEqual(final.away_team_id, w2.id)


class GameScoringTests(TestCase):
    """Stage E: standings use each game's own points config."""

    def test_cricket_seed_exists(self):
        cricket = Game.objects.filter(name="Cricket").first()
        self.assertIsNotNone(cricket)
        self.assertEqual(cricket.points_win, 2)
        self.assertEqual(cricket.score_noun, "runs")

    def _played_league(self, game):
        # 3 teams: Team 1 beats 2 and 3; Team 2 beats 3.
        title = f"{game.name} Cup" if game else "No-game Cup"
        t = make_tournament(3, title=title, game=game)
        services.generate_league_fixtures(t)
        for m in Match.objects.filter(Match_Tournament=t):
            names = {m.home_team.name, m.away_team.name}
            if names == {"Team 1", "Team 2"}:
                self._win(m, "Team 1")
            elif names == {"Team 1", "Team 3"}:
                self._win(m, "Team 1")
            elif names == {"Team 2", "Team 3"}:
                self._win(m, "Team 2")
        return services.compute_standings(t)

    def _win(self, match, winner_name):
        if match.home_team.name == winner_name:
            services.record_result(match, 2, 1)
        else:
            services.record_result(match, 1, 2)

    def test_football_uses_three_points(self):
        football = Game.objects.get(name="Turf Football")
        rows = self._played_league(football)
        self.assertEqual(rows[0]["points"], 6)   # 2 wins * 3
        self.assertEqual(rows[1]["points"], 3)   # 1 win * 3

    def test_cricket_uses_two_points(self):
        cricket = Game.objects.get(name="Cricket")
        rows = self._played_league(cricket)
        self.assertEqual(rows[0]["points"], 4)   # 2 wins * 2
        self.assertEqual(rows[1]["points"], 2)   # 1 win * 2

    def test_no_game_defaults_to_three_points(self):
        rows = self._played_league(None)
        self.assertEqual(rows[0]["points"], 6)
