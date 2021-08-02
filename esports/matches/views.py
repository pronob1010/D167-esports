from django.shortcuts import render

# Create your views here.
def matches(request):
    return render(request, 'matches/matches.html', {})

def liveMatches(request):
    return render(request, 'matches/matchlive.html', {})

def upCommingMatches(request):
    return render(request, 'matches/upcomingmatch.html', {})