from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from users.forms import UserRegisteration
from ewaste_management.models import University, Organization, User
from ewaste_management.forms import OrganizationForm




# Create your views here.
def index(request):
    return render(request, "users/index.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("ewaste_management:dashboard"))
        else:
            return render(request, "users/login.html", {
                "message": "Invalid credentails"
            })
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request=request)
    return render(request, 'users/logout.html')

def registration(request):
    if request.method == "POST":
        if request.POST.get("organization_name") != "":
            form = OrganizationForm(request.POST)
            if form.is_valid():
                form.save()
            else:
                universities = University.objects.all()
                organizations = Organization.objects.all()
                return render(request, "users/register.html", {
                    "message": form.errors,
                    "universities": universities,
                    "organizations": organizations               
                })
        form = UserRegisteration(request.POST, request.FILES)
        if form.is_valid():
            user = User()
            user.email = form.cleaned_data["email"]
            user.username = form.cleaned_data["username"]
            if request.POST.get("university") != "":
                user.university = University.objects.get(id=request.POST.get("university"))
            if request.POST.get("organization") != "" and request.POST.get("organization"):
                user.organization = Organization.objects.get(id=request.POST.get("organization"))
            elif request.POST.get("organization_name") != "":
                user.organization = Organization.objects.get(organization_name=request.POST.get("organization_name"))
            user.phone_number = form.cleaned_data["phone_number"]
            user.set_password(form.cleaned_data["password"])
            user.role = form.cleaned_data["role"]
            user.bio = form.cleaned_data["bio"]
            user.save()
            return HttpResponseRedirect(reverse("users:login"))
        else:
            universities = University.objects.all()
            organizations = Organization.objects.all()
            return render(request, "users/register.html", {
                "message": form.errors,
                "universities": universities,
                "organizations": organizations               
            })
    elif request.method == "GET":
        universities = University.objects.all()
        organizations = Organization.objects.all()
        return render(request, "users/register.html", {
            "universities": universities, 
            "organizations": organizations
        })