from matches . models import *
from administration . models import SiteInfo
def extras(request):
    site_data = SiteInfo.objects.get(id=1)
    match_data = MatchGroup.objects.all()

    # unique_tournament = []
    # for t in match_data:
    #     t_li = []

    #     if t.Tournament.slug not in t_li:
    #         t_li.append(t.Tournament.slug)
    #         t_li.append(t.Tournament.Tournament_title)

    #         season = SEASON.objects.filter(Tournament__slug = t.Tournament.slug)
    #         unique_season = {}
    #         for s in season:
    #             li = []
    #             if s.slug not in li:
    #                 li.append(s.slug)
    #                 li.append(s.SEASON_title)
                    
    #                 round = MatchRound.objects.filter(Season__slug=s.slug)
    #                 rounds = {}
    #                 for r in round:
    #                     if r.slug not in rounds:
    #                         rounds[r.slug] = r.Round_title
    #                 li.append(rounds)

    #             unique_season[s.slug] = li
    #         if unique_season not in t_li:
    #             t_li.append(unique_season)
        
    #     if t_li not in unique_tournament:
    #         unique_tournament.append(t_li)

    # print(unique_tournament)

    #  <ul>
    #                             {% for t in unique_tournament %}
    #                             <li class="">
    #                                 <a href="{% url "table" t.0 %}"><span>{{t.1}}</span></a>
    #                                 <ul>
    #                                     {% for k, v in t.2.items %}
    #                                     <li class="">
    #                                         <a href="{% url "table" k %}"><span>{{v.1}}</span></a>
    #                                         <ul>
    #                                             {% for k1,v2 in v.2.items %}
    #                                             <li class="">
    #                                                 <a href=""><span>{{v2}}</span></a>
    #                                             </li>
    #                                             {% endfor %}
    #                                         </ul>
    #                                     </li>
    #                                     {% endfor %}
    #                                 </ul>
    #                             </li>
    #                             {% endfor %}

    #                             <li><a href="{% url 'live' %}"><span>Stream</span></a></li>

    #                             <li><a href="{% url 'upcoming' %}"><span>upcoming match</span></a></li>

    #                             <li><a href="#"><span>tournament registration </span></a></li>
    #                         </ul>
        
            
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


    # return {"unique_tournament":unique_tournament,"site_data":site_data}
    return {"nav_season":unique_season,"site_data":site_data}
    # return {}