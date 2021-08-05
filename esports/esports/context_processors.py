from matches . models import *
def extras(request):
    match_data = MatchGroup.objects.all()
    unique_season = []
    for s in match_data:
        li = []
        if s.Season.slug not in li:
            li.append(s.Season.slug)
            li.append(s.Season.SEASON_title)

            round= MatchRound.objects.filter(Season__slug=s.Season.slug)
            rounds = {}
            for r in round:
                if r.slug not in rounds:
                    rounds[r.slug]=r.Round_title
            li.append(rounds)
        if li not in unique_season:
            unique_season.append(li)
    return {"nav_season":unique_season,}