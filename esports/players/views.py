from django.shortcuts import render
from.models import *
# Create your views here.
def player(request):
    return render(request, 'player/player.html', {})