from django.urls import path 
from . views import *
urlpatterns = [
    path('signup/', userSignup, name="signup"),
    path('login/', loginUser, name="login"),
    path('logout/', logoutUser, name="logout"),
]
