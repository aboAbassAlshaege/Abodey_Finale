from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

def search(request):
    return

def index(request):
    return render(request, 'library/index.html')

# Authentication views
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "library/login.html", {
                "message": "Username or password is invalid."
            })
    else:
        return render(request, 'library/login.html')
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
    
def signup_view(request):
    if request.method == "POST":
        #####################################
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password_confirmation = request.POST["password_confirmation"]
        # password confirmation
        if password != password_confirmation:
            return render(request, "library/signup.html", {
                "message": "Passwords must match"
            })
        # now try to create a user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "library/signup.html", {
                "message": "Username already taken"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
        
    else:
        return render(request, 'library/signup.html')