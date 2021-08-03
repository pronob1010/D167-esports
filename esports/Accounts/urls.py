from django.urls import path 
from . views import *
urlpatterns = [
    path('signup/', userSignup, name="signup"),
]
