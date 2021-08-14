from django.contrib import admin
from django.shortcuts import render

from . models import *
from matches .models import *
from Accounts. models import *
# Create your views here.
def index(request):
    indexdata = SiteInfo.objects.all()
    Legend = LegendZone.objects.get(id=1)
    site_social_media = SocialMediaLinks.objects.all()

    for i in indexdata:
        index_data= i
    
    featured = Match.objects.filter(Featured = True)[:1]
    featured1 = Match.objects.filter(Featured = True)[1:]
    # print(featured)

    stuff = []
    stuff_data = SubAdminCategories.objects.all()
    for i in stuff_data:
        item_dic = {}
        admins_data = SubAdmin.objects.filter(categories__slug = i.slug)
        if admins_data.exists():
            admin_li = []
            for sadmin in admins_data:
                pair_list = []
                pair_list.append(sadmin.user.id)
                pair_list.append(sadmin.user.username)
                img = User.objects.get(username = sadmin.user.username).photo
                pair_list.append(img)

                admin_li.append(pair_list)
            # print(admin_li)
            item_dic[i] = admin_li

            stuff.append(item_dic)
    print(stuff)

    context = {
        'index_data' : index_data,
        'featured':featured,
        'featured1':featured1,
        'Legend':Legend,
        'site_social_media':site_social_media,
        'stuff':stuff, 
        }

    return render(request, 'administration/index.html', context)




def liveMatches(request):
    broadcast_data = broadcast.objects.all()
    context = {
        "broadcast_data":broadcast_data,
    }
    return render(request, 'matches/matchlive.html', context)


def contact(request):
    site_about = SiteAbout.objects.all()
    maindata = SiteInfo.objects.all()
    site_social_media = SocialMediaLinks.objects.all()

    context = {
        'site_about':site_about,
        'maindata':maindata,
        'site_social_media':site_social_media,
    }
    return render(request, 'administration/contacts.html', context)

def about(request):
    site_about = SiteAbout.objects.all()
    site_achivment = Top_achivment.objects.all()
    sponsor = sponsor_details.objects.all()

    context = {
        'site_about':site_about,
        'site_achivment':site_achivment,
        'sponsor':sponsor,
    }
    return render(request, 'administration/about.html', context)