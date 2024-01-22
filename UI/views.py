from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

import pandas as pd
import requests, json

def home(request):
    if request.method == 'POST':
        cmpnyname = request.POST.get("cmpnyname")
        return redirect("cmpny", cmpnyname=cmpnyname)
    return render(request, "home.html")

def cmpny(request, cmpnyname):
    basic_info = requests.post("http://localhost:8000/api/basicInfo", data={"cmpnyname":cmpnyname})
    if basic_info.status_code != 200:
        return redirect("not_found")
    basic_info = basic_info.json() #dict

    finstate_sum = requests.post("http://localhost:8000/api/finstateSum", data={"cmpnyname":cmpnyname})
    if finstate_sum.status_code != 200:
        return redirect("not_found")
    finstate_sum = finstate_sum.json() #dict
    print(finstate_sum)
    keys = list(finstate_sum[0].keys())
    print(keys)

    return render(request, "cmpny.html", {"basic_info":basic_info, "finstate_sum":finstate_sum, "keys":keys})

def not_found(request):
    return render(request, "not_found.html")