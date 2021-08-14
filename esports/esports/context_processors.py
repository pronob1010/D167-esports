from matches . models import *
from administration . models import *
from teams . models import *
def extras(request):
    sitedata = SiteInfo.objects.all()
    site_social_media = SocialMediaLinks.objects.all()
    maindata = SiteInfo.objects.all()
    site_about = SiteAbout.objects.all()
    our_teams = CentralTeam.objects.all()

    for i in sitedata:
        site_data = i
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
        context = {

            "our_teams":our_teams,
            "site_about":site_about,
            "maindata":maindata,
            "site_social_media":site_social_media,
            "nav_Tournament":unique_Tournament,
            "site_data":site_data
        }
        return context 
    else:
        return {}