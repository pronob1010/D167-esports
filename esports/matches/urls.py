from django.contrib import admin
from django.urls import path
from. import views
urlpatterns = [
    # path('matches/', views.matches, name="matches"),
    path('upcoming/', views.upCommingMatches, name="upcoming"),
    path('table/<str:slug>/', views.data_table, name="table"),
    path('rank-list/<str:slug>/', views.rankList, name="ranklist"),
]
