from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('administration.urls')),
    path('play/', include('matches.urls')),
    path('players/', include('players.urls')),
    path('teams/', include('teams.urls')),
    path('account/', include('Accounts.urls')),
    path('chaining/', include('smart_selects.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)