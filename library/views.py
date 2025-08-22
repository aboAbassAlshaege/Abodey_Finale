from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import asyncio
import httpx
from urllib.parse import quote

# Create your views here.
def index(request):
    return render(request, 'library/index.html')

############## api ################
# Gutenberg project
async def gutenberg_fetch(title):
    url = f"https://gutendex.com/books/?search={title}"
    async with httpx.AsyncClient(timeout=20.0) as clinet:
        r = await clinet.get(url)
        if r.status_code == 200:
            data = r.json()
            return [
                {
                    "title": book.get("title"),
                    "authors": [author.get("name") for author in book.get("authors")] if book.get("authors") else ["Unknown"],
                    "source": "Gutenberg Project",
                    "url": f"https://gutenberg.org/ebooks/{book.get("id")}"
                } for book in data["results"][:5]
            ]
    return []
# Open Library
async def openlibrary_fetch(title):
    url = f"https://openlibrary.org/search.json?q={title}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json()
            return [
                {"source": "Open Library",
                 "title": doc.get("title"),
                 "authors": doc.get("author_name", ["Unknown"]),
                 "url": f"archive.org/details/{doc.get('ia')[0]}" if doc.get("ia") else None
                } for doc in data["docs"][:5]
            ]
    return []
# Combine resources
async def cobine_tasks(title):
    gutenberg_task = gutenberg_fetch(title)
    openlibrary_task = openlibrary_fetch(title)
    results = await asyncio.gather(gutenberg_task, openlibrary_task)
    return [book for fetch_result in results for book in fetch_result]

# api endpoint
def search(request):
    title = request.GET.get("title")
    if title:
        encoded_title = quote(title)
        results = asyncio.run(cobine_tasks(encoded_title))
        return JsonResponse({"title": title, "results": results})
    else:
        return JsonResponse({"message": "Invalid book title", "status_code": 400})
##########################################
    
    



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