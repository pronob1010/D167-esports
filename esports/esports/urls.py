from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('administration.urls')), # Global: main landing, etc.
    path('players/', include('players.urls')), # Global: public player profiles
    path('account/', include('Accounts.urls')), # Global: login, signup
    path('chaining/', include('smart_selects.urls')), # Global: smart_selects functionality

    # Tenant-specific URLs
    path('t/<str:tenant_slug>/play/', include('matches.urls')),
    path('t/<str:tenant_slug>/teams/', include('teams.urls')),
    # If parts of 'administration' become tenant-specific, they'd need a similar prefix
    # e.g., path('t/<str:tenant_slug>/dashboard/', include('administration.dashboard_urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)