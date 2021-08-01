from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('administration.urls')),
    path('matches/', include('matches.urls')),
    path('players/', include('players.urls')),
    path('teams/', include('teams.urls')),
]
