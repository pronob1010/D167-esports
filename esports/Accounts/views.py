from django.shortcuts import render

from . forms import UserCreationForms

def userSignup(request):
    form = UserCreationForms()
    return render(request, 'accounts/signup.html', {'form':form})