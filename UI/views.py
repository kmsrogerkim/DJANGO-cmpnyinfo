from django.shortcuts import render, redirect

import plotly.graph_objects as go
import pandas as pd
import requests

def home(request):
    if request.method == 'POST':
        cmpnyname = request.POST.get("cmpnyname")
        print("WORKS TILL HERE: home-if")
        return redirect("cmpny", cmpnyname=cmpnyname)
    print("WORKS TILL HERE: home")
    return render(request, "home.html")

def cmpny(request, cmpnyname):
    print("WORKS TILL HERE: cmpny-got the request")
    if request.method == 'POST':
        cmpnyname = request.POST.get("cmpnyname")
        return redirect("cmpny", cmpnyname=cmpnyname)
    
    #Calling API
    basic_info = requests.get(f"http://localhost:8000/api/basicInfo/{cmpnyname}")
    if basic_info.status_code == 404:
        return redirect("not_found")
    finstate_sum = requests.get(f"http://localhost:8000/api/finstateSum/{cmpnyname}")
    graph_data = requests.get(f"http://localhost:8000/api/graphData/{cmpnyname}")
    print("WORKS TILL HERE!")
    if basic_info.status_code != 200 or finstate_sum.status_code != 200 or graph_data.status_code != 200:
        return redirect("error-page")
    basic_info = basic_info.json() #dict
    finstate_sum = finstate_sum.json() #dict
    keys = list(finstate_sum[0].keys())
    graph_data = graph_data.json() #dict

    #BOX PLOT
    box_plot_data = graph_data["box_plot_data"]
    box_plot_data = pd.DataFrame(box_plot_data)
    graph_val = []
    labels = ["P_Contd", "L_Contd", "P_Turned", "L_Turned"]
    for state in labels:
        value = box_plot_data[box_plot_data["Operating_Income(added)_Profit_Status"] == state]
        if value.empty:
            graph_val.append([0])
        else:
            graph_val.append(list(value["Profit"]))    
    #Drawing with Plotly
    fig = go.Figure()
    for i in range(4):
        fig.add_trace(go.Box(y=graph_val[i], name=labels[i]))
    box_plot = fig.to_html()

    #Number
    number_data = graph_data["number_data"] #dict {"Year":[2019,...], "a":[...]}
    years = number_data.pop("Year")
    number_graph = draw_line_graph(years, graph_data=number_data)
    
    #Ratio
    ratio_data = graph_data["ratio_data"] #dict {"Year":[2019,...], "a":[...]}
    ratio_graph = draw_line_graph(years, graph_data=ratio_data)

    return render(request, "cmpny.html", {"basic_info":basic_info, "finstate_sum":finstate_sum, "keys":keys, "box_plot":box_plot, "number_graph":number_graph, "ratio_graph":ratio_graph})

def about(request):
    cmpny_list = requests.get("http://localhost:8000/api/cmpnyList")
    cmpny_list = cmpny_list.json()
    return render(request, "about.html", {"cmpny_list":cmpny_list["cmpny_list"]})

def draw_line_graph(x: list, graph_data:dict):
    traces = []
    for key, val in graph_data.items():
        traces.append(go.Scatter(x=x, y=val, name=key))
    layout = go.Layout(xaxis=dict(title='Year'), yaxis=dict(title='Stats'), width=550)
    fig = go.Figure(data=traces, layout=layout)
    return fig.to_html()

def not_found(request):
    return render(request, "not_found.html")

def error_page(request):
    return render(request, "error_page.html")