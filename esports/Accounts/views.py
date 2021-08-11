from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . forms import SignUpForm


from django.contrib.auth import login, authenticate, logout

def userSignup(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    return render(request, 'accounts/signup.html', {'form':form})

def loginUser(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username = username, password = password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
    return render(request, 'accounts/login.html', {'form':form})
    
from django.contrib.auth.decorators import login_required
@login_required
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))