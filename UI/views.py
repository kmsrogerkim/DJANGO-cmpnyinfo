from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RegisterForm
import requests, json

def home(request):
    if request.method == 'POST':
        cmpnyname = request.POST.get("cmpnyname")
        return redirect("cmpny", cmpnyname=cmpnyname)
    return render(request, "home.html")

# def sign_up(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             usernamev = request.POST.get('username')
#             passwordv = request.POST.get('password2')
#             user = authenticate(username = usernamev, password = passwordv)
#             login(request, user)
#             return redirect("home")
#     else:
#         form = RegisterForm()
#         return render(request, "sign_up.html", {"form":form})
#     return render(request, "sign_up.html", {"form":form})

# def sign_in(request):
#     if request.method == 'POST':
#         usernamev = request.POST.get('username')
#         passwordv = request.POST.get('password')
#         user = authenticate(request, username=usernamev, password = passwordv)
#         if user is not None:
#             login(request, user)
#             return redirect("home")
#         else:
#             messages.success(request, "Incorrect password/username. Please TRY AGAIN!")
#             return redirect("sign_in")
#     else:
#         return render(request, "sign_in.html")

def cmpny(request, cmpnyname):
    basic_info = requests.post("http://localhost:8000/API/basicInfo", data={"cmpnyname":cmpnyname})
    if basic_info.status_code != 200:
        return redirect("not_found")
    basic_info = basic_info.json() #dict
    return render(request, "cmpny.html", {"basic_info":basic_info})

def not_found(request):
    return render(request, "not_found.html")