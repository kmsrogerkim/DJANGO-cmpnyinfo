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
#Getting basic_info.csv
file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'basic_info.csv') 
basic_info_csv = pd.read_csv(file_path, encoding='euc-kr')

@api_view(['POST'])
def get_basic_info(request):
    '''
    Argument: POST http request
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

    return Response(basic_info)

@api_view(['POST'])
def get_finstate_sum(request):
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]
    try:
        df = basic_info_csv[basic_info_csv["Company_Name"] == cmpnyname]
        if df["Total_Assets"].iloc[0] == np.nan:
            print("~" * 100)
            raise custom_exceptions.YoungCmpny
    except Exception as e:
        print(e)
        return Response({"error": "Bad Request: YoungCmpny"}, status=status.HTTP_400_BAD_REQUEST)

    #Dropping unnecessary infos
    df.drop(["Revenue_Profit_Status", "Operating_Income(added)_Profit_Status", "Net_Income(added)_Profit_Status"], axis=1, inplace=True)

    #Convert df to dict
    finstate_sum = df.to_dict(orient="records")

    return Response(finstate_sum)