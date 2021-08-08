from django.shortcuts import render

from . models import *
from matches .models import *
# Create your views here.
def index(request):
    index_data = SiteInfo.objects.get(id=1)
    featured = Match.objects.filter(Featured = True)[:1]
    featured1 = Match.objects.filter(Featured = True)[1:]
    print(featured)
    context = {
        'index_data' : index_data,
        'featured':featured,
        'featured1':featured1,
        }
   
    return render(request, 'administration/index.html', context)

def contact(request):
    return render(request, 'administration/contacts.html', {})