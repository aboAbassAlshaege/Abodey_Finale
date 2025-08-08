from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'library/index.html')

# Authentication views
def login_view(request):
    if request.method == "POST":
        return
    else:
        return render(request, 'library/login.html')
    
def signup_view(request):
    if request.method == "POST":
        return
    else:
        return render(request, 'library/signup.html')