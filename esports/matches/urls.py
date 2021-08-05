from django.contrib import admin
from django.urls import path
from. import views
urlpatterns = [
    # path('matches/', views.matches, name="matches"),
    path('live/', views.liveMatches, name="live"),
    path('upcoming/', views.upCommingMatches, name="upcoming"),
    path('table/<str:slug>/', views.data_table, name="table"),
]
