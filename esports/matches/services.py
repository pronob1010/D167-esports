"""Fixture generation and standings - pure-ish helpers used by organizer views.

Kept out of views so the tournament logic is unit-testable on its own.
Everything here operates on the existing Tournament -> MatchRound -> Match
hierarchy plus the two-sided result fields on Match.
"""
import math

from .models import Match, MatchRound, Tournament, TournamentTeam


def clear_fixtures(tournament):
    """Remove any previously generated rounds/matches for a clean regenerate."""
    Match.objects.filter(Match_Tournament=tournament).delete()
    MatchRound.objects.filter(Tournament=tournament).delete()


def _seeding_order(bracket_size):
    """Standard single-elimination seed slot order for a power-of-two bracket.

    e.g. size 8 -> [1, 8, 4, 5, 2, 7, 3, 6]. Using this to place teams means
    byes (the missing high seed numbers) are spread out against the top seeds
    instead of clustering into one empty match.
    """
    seeds = [1]
    while len(seeds) < bracket_size:
        size = len(seeds) * 2
        seeds = [s for pair in ((x, size + 1 - x) for x in seeds) for s in pair]
    return seeds


def _round_name_for_match_count(match_count):
    """Human name for a knockout round given how many matches it holds."""
    teams_in_round = match_count * 2
    names = {2: "Final", 4: "Semi-final", 8: "Quarter-final"}
    return names.get(teams_in_round, f"Round of {teams_in_round}")


def generate_league_fixtures(tournament):
    """Single round-robin (everyone plays everyone once) via the circle method.

    Returns the number of matches created.
    """
    clear_fixtures(tournament)
    teams = list(tournament.teams.all())
    if len(teams) < 2:
        return 0

    arr = teams[:]
    if len(arr) % 2:
        arr.append(None)  # odd count -> one team rests each matchday (bye)
    n = len(arr)
    half = n // 2

    created = 0
    for r in range(n - 1):
        matchday = MatchRound.objects.create(
            Tournament=tournament, Round_title=f"Matchday {r + 1}"
        )
        order = 0
        for i in range(half):
            a, b = arr[i], arr[n - 1 - i]
            if a is not None and b is not None:
                Match.objects.create(
                    Match_Title=f"{a.name} vs {b.name}",
                    Match_Tournament=tournament,
                    Match_Round=matchday,
                    home_team=a,
                    away_team=b,
                    order=order,
                )
                created += 1
                order += 1
        # Rotate all but the first entry (standard circle method).
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    return created


def generate_knockout_fixtures(tournament):
    """Single-elimination bracket with byes for non-power-of-two team counts.

    Pre-creates every round and links each match to the one its winner feeds
    into, so entering a score automatically advances the winner. Returns the
    number of matches created.
    """
    clear_fixtures(tournament)
    teams = list(tournament.teams.all())
    if len(teams) < 2:
        return 0

    bracket_size = 2 ** math.ceil(math.log2(len(teams)))
    # Place teams into bracket slots by standard seeding so byes (missing high
    # seeds) are distributed against the top seeds rather than clustered.
    order = _seeding_order(bracket_size)
    slots = [teams[rank - 1] if rank <= len(teams) else None for rank in order]

    # Build rounds from first round down to the final.
    rounds = []  # list of lists of Match
    match_count = bracket_size // 2
    prev_round = None
    while match_count >= 1:
        rnd = MatchRound.objects.create(
            Tournament=tournament,
            Round_title=_round_name_for_match_count(match_count),
        )
        this_round = []
        for i in range(match_count):
            m = Match.objects.create(
                Match_Title=f"{rnd.Round_title} #{i + 1}",
                Match_Tournament=tournament,
                Match_Round=rnd,
                order=i,
            )
            this_round.append(m)
        # Link previous round's matches into this one.
        if prev_round is not None:
            for j, feeder in enumerate(prev_round):
                feeder.next_match = this_round[j // 2]
                feeder.next_match_slot = "home" if j % 2 == 0 else "away"
                feeder.save(update_fields=["next_match", "next_match_slot"])
        rounds.append(this_round)
        prev_round = this_round
        match_count //= 2

    # Seed the first round from the slot list.
    first = rounds[0]
    created = sum(len(r) for r in rounds)
    for i, m in enumerate(first):
        m.home_team = slots[2 * i]
        m.away_team = slots[2 * i + 1]
        m.save(update_fields=["home_team", "away_team"])

    # Resolve byes: a first-round match with exactly one team auto-advances it.
    for m in first:
        present = None
        if m.home_team and not m.away_team:
            present = m.home_team
        elif m.away_team and not m.home_team:
            present = m.away_team
        if present is not None:
            m.is_played = True
            m.save(update_fields=["is_played"])
            _advance_winner(m, present)
    return created


def _advance_winner(match, team):
    """Place ``team`` into the slot of the match this one feeds into."""
    nm = match.next_match
    if not nm or team is None:
        return
    if match.next_match_slot == "away":
        nm.away_team = team
    else:
        nm.home_team = team
    nm.save(update_fields=["home_team", "away_team"])


def record_result(match, home_score, away_score):
    """Save a two-sided result and, for knockouts, advance the winner."""
    match.home_score = home_score
    match.away_score = away_score
    match.is_played = True
    match.save(update_fields=["home_score", "away_score", "is_played"])
    winner = match.winner
    if match.next_match_id and winner is not None:
        _advance_winner(match, winner)
    return match


def compute_standings(tournament):
    """League table from played two-sided matches. Returns rows sorted best-first.

    Each row: team, played, won, drawn, lost, gf, ga, gd, points (3/1/0).
    """
    table = {}
    for t in tournament.teams.all():
        table[t.id] = {
            "team": t, "played": 0, "won": 0, "drawn": 0, "lost": 0,
            "gf": 0, "ga": 0, "gd": 0, "points": 0,
        }

    played = Match.objects.filter(
        Match_Tournament=tournament, is_played=True,
        home_team__isnull=False, away_team__isnull=False,
        home_score__isnull=False, away_score__isnull=False,
    ).select_related("home_team", "away_team")

    for m in played:
        h, a = table.get(m.home_team_id), table.get(m.away_team_id)
        if h is None or a is None:
            continue
        h["played"] += 1
        a["played"] += 1
        h["gf"] += m.home_score
        h["ga"] += m.away_score
        a["gf"] += m.away_score
        a["ga"] += m.home_score
        if m.home_score > m.away_score:
            h["won"] += 1; h["points"] += 3; a["lost"] += 1
        elif m.away_score > m.home_score:
            a["won"] += 1; a["points"] += 3; h["lost"] += 1
        else:
            h["drawn"] += 1; a["drawn"] += 1
            h["points"] += 1; a["points"] += 1

    rows = list(table.values())
    for row in rows:
        row["gd"] = row["gf"] - row["ga"]
    rows.sort(key=lambda r: (r["points"], r["gd"], r["gf"], r["team"].name), reverse=True)
    return rows
