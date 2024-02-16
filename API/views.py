from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .api_local import cmpny_data
from .api_local import custom_exceptions

from tabulate import tabulate
import pandas as pd
import numpy as np
import pickle, os

#Getting name_code.pkl
file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl') 
with open(file_path, 'rb') as f:
    name_code = pickle.load(f)
cmpny_list = list(name_code.keys())
#Getting basic_info.csv
file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'basic_info.csv') 
basic_info_csv = pd.read_csv(file_path, encoding='euc-kr')
#Getting basic_info_for_analysis.csv
file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'basic_info_for_analysis.csv') 
cols = ["Company_Name", "Year", "Current_Stock", "Future_Stock", "Operating_Income(added)_Profit_Status","Net_Income(added)_Profit_Status" ]
bf_analysis_csv = pd.read_csv(file_path, usecols=cols, encoding='euc-kr')

def format_large_number(number: int) -> str:
    suffixes = ['', 'k', 'M', 'B', 'T']
    magnitude = 0

    while abs(number) >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        number /= 1000

    formatted_number = '{:.1f}{}'.format(number, suffixes[magnitude])
    return formatted_number

def convert_finstate_sum_large_num(finstate_sum: list):
    '''
    Argument: list of dictionaries
    '''
    for dicts in finstate_sum:
        for key, val in dicts.items():
            if isinstance(val, float):
                dicts[key] = format_large_number(val)

@api_view(['POST'])
def get_basic_info(request):
    '''
    Returns: basic stock info of the cmpny
    '''
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]
    try:
        cmpnycode = name_code[cmpnyname]
    except KeyError:
        return Response({"error": "Bad Request: cmpnyname not in list"}, status=status.HTTP_400_BAD_REQUEST)

    basic_info = cmpny_data.get_stock_info(cmpnycode) #dict
    basic_info["cmpnyname"] = cmpnyname #setting the company name to the posted company name

    stock_num = basic_info_csv.loc[(basic_info_csv["Company_Name"] == cmpnyname), "Stock_Num"].iloc[5] #int
    market_cap = format_large_number(stock_num * basic_info["Yesterday"])
    basic_info["market_cap"] = market_cap 
    return Response(basic_info)

@api_view(['POST'])
def get_finstate_sum(request):
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]

    try:
        df = cmpny_data.get_cmpny_df(basic_info_csv, cmpnyname)
    except custom_exceptions.YoungCmpny as e:
        return Response({"error": "Bad Request: YoungCmpny"}, status=status.HTTP_400_BAD_REQUEST)
    #Dropping unnecessary infos
    df = df.drop(["Revenue_Profit_Status", "Operating_Income(added)_Profit_Status", "Net_Income(added)_Profit_Status", "Stock_Num"], axis=1)

    #Convert df to dict
    finstate_sum = df.to_dict(orient="records")
    convert_finstate_sum_large_num(finstate_sum) #format large numbers (sth like 115000000000 to 11.5T)
    return Response(finstate_sum)

@api_view(['POST'])
def get_graph_data(request):
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]

    try:
        #Initializing dfs
        boxPlot_df = cmpny_data.get_cmpny_df(bf_analysis_csv, cmpnyname)

        number_df = cmpny_data.get_cmpny_df(basic_info_csv, cmpnyname)
        ratio_df = number_df[["Debt_Equity_Ratio", "PER", "ROA", "ROE"]]
        number_df = number_df[["Year", "Total_Assets", "Total_Debt", "Total_Equity", "Revenue", "Operating_Income(added)", "Net_Income(added)"]]
    except custom_exceptions.YoungCmpny as e:
        return Response({"error": "Bad Request: YoungCmpny"}, status=status.HTTP_400_BAD_REQUEST)
    
    if "Profit" not in boxPlot_df:
        boxPlot_df.loc[:, ["Profit"]] = (boxPlot_df["Current_Stock"] - boxPlot_df["Future_Stock"]) / boxPlot_df["Current_Stock"] * 100

    #Convert dfs to dict
    response = {
    "box_plot_data": boxPlot_df.to_dict(orient="records"),
    "ratio_data": ratio_df.to_dict(orient="list"),
    "number_data": number_df.to_dict(orient="list"),
    }
    return Response(response)

@api_view(['GET'])
def get_cmpny_list(request):
    global cmpny_list
    response = {"cmpny_list":cmpny_list}
    return Response(response)