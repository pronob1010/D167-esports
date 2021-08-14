from django.urls import path
from. import views
urlpatterns = [
    path('teams/', views.teams, name="teams"),
    path('team-details/<str:slug>', views.teamdetails, name="teamdetails"),
]
