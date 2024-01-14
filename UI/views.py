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

def cmpny(request, cmpnyname):
    basic_info = requests.post("http://localhost:8000/API/basicInfo", data={"cmpnyname":cmpnyname})
    if basic_info.status_code != 200:
        return redirect("not_found")
    basic_info = basic_info.json() #dict
    return render(request, "cmpny.html", {"basic_info":basic_info})

def not_found(request):
    return render(request, "not_found.html")