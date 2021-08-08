from matches . models import *
from administration . models import SiteInfo
def extras(request):
    site_data = SiteInfo.objects.get(id=1)
    match_data = MatchGroup.objects.all()
# ---------------------------------
    # unique_tournament = []
    # for t in match_data:
    #     t_li = []

    #     if t.Tournament.slug not in t_li:
    #         t_li.append(t.Tournament.slug)
    #         t_li.append(t.Tournament.Tournament_title)

    #         Tournament = Tournament.objects.filter(Tournament__slug = t.Tournament.slug)
    #         unique_Tournament = {}
    #         for s in Tournament:
    #             li = []
    #             if s.slug not in li:
    #                 li.append(s.slug)
    #                 li.append(s.Tournament_title)
                    
    #                 round = MatchRound.objects.filter(Tournament__slug=s.slug)
    #                 rounds = {}
    #                 for r in round:
    #                     if r.slug not in rounds:
    #                         rounds[r.slug] = r.Round_title
    #                 li.append(rounds)

    #             unique_Tournament[s.slug] = li
    #         if unique_Tournament not in t_li:
    #             t_li.append(unique_Tournament)
        
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
        
    # ------------------------------------------   
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
    return {"nav_Tournament":unique_Tournament,"site_data":site_data}
    # return {}