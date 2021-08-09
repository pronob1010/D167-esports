from django.urls import path
from. import views
urlpatterns = [
    path('player/<str:slug>', views.player, name="player"),
]
