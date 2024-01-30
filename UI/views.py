from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect

from tabulate import tabulate
import plotly.express as px
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
    keys = list(finstate_sum[0].keys())

    graph_data = requests.post("http://localhost:8000/api/graphData", data={"cmpnyname":cmpnyname})
    if graph_data.status_code != 200:
        return redirect("not_found")
    graph_data = graph_data.json() #dict
    graph_data = pd.DataFrame(graph_data)

    graph_val = []
    labels = ["P_Contd", "L_Contd", "P_Turned", "L_Turned"]
    for state in labels:
        value = graph_data[graph_data["Operating_Income(added)_Profit_Status"] == state]
        if value.empty:
            graph_val.append([0])
        else:
            graph_val.append(value["Profit"])    

    print(type(graph_val))
    print(graph_val)
    # Create a box plot using Plotly Express
    fig = px.box(graph_val, labels=labels)
    fig.update_yaxes(range=[-100, 100])
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=[1, 2, 3, 4], ticktext=labels),
        yaxis_title="Profit"
    )
    graph = fig.to_html()

    return render(request, "cmpny.html", {"basic_info":basic_info, "finstate_sum":finstate_sum, "keys":keys, "graph":graph})

def not_found(request):
    return render(request, "not_found.html")