from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.views.static import serve as media_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('administration.urls')),
    path('play/', include('matches.urls')),
    path('players/', include('players.urls')),
    path('teams/', include('teams.urls')),
    path('account/', include('Accounts.urls')),
    path('organizer/', include('organizers.urls')),
    path('chaining/', include('smart_selects.urls')),
]

# Serve user-uploaded media. Django's static() helper only serves when DEBUG,
# so use an explicit route that also works in production (point MEDIA_ROOT at a
# persistent Railway volume). WhiteNoise handles /static/ separately.
urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        media_serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
