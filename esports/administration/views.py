from django.shortcuts import render

from . models import *
# Create your views here.
def index(request):
    
    index_data = SiteInfo.objects.get(pk=1)

    context = {
        'index_data' : index_data
    }
    return render(request, 'index.html', context)