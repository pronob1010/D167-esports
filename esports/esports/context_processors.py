from matches . models import *
from administration . models import SiteInfo
def extras(request):
    site_data = SiteInfo.objects.get(id=1)
    match_data = MatchGroup.objects.all()
    
    unique_Tournament = []
    for s in match_data:
        li = []
        if s.Tournament.slug not in li:
            li.append(s.Tournament.slug)
            li.append(s.Tournament.Tournament_title)
            
            round= MatchRound.objects.filter(Tournament__slug=s.Tournament.slug)
            rounds = {}
            for r in round:
                if r.slug not in rounds:
                    rounds[r.slug]=r.Round_title
            li.append(rounds)
            li.append(s.Tournament.mvp_expected)
        if li not in unique_Tournament:
            unique_Tournament.append(li)


    # return {"unique_tournament":unique_tournament,"site_data":site_data}
    if site_data is not None:
        return {"nav_Tournament":unique_Tournament,"site_data":site_data}
    else:
        return {}