'''
This file works as a connecting bridge between the server layer and this(local) layer of the API function.
It is equivalent of the 'lib_one.py' file, but for the server layer(django's views.py file)
The 'lib_one.py' file is exclusivly used by/for the local_api layer.
'''
from .import lib_one

from rest_framework.response import Response
from rest_framework import status

from . import custom_exceptions

import FinanceDataReader as fdr
from tabulate import tabulate
import pandas as pd
import pandas as pd
import numpy as np

def get_stock_info(cmpnycode: str) -> dict:
    '''
    Returns: yesterday's stock info; high/low in 52 weeks
    '''
    today = lib_one.GetDateToday()
    start_date = today - pd.to_timedelta(364, 'D') #52 weeks prior
    sp_data = fdr.DataReader(cmpnycode, start=start_date, end=today) #dataframe

    yesterday_info = lib_one.GetDetailStockPrice(sp_data, today)
    high, low = get_hl(sp_data)

    ans = {
        "Yesterday":yesterday_info["Close"],
        "Y_high":yesterday_info["High"],
        "Y_low":yesterday_info["Low"],
        "F_high":high,
        "F_low":low
    }
    return ans

def get_hl(sp_data: pd.DataFrame) -> dict:
    '''
    Returns: the highest and lowest stock price in the sp_data
    '''
    stock_prices = sp_data["Close"]
    stock_prices = stock_prices.sort_values(ascending=False)

    high = stock_prices.iloc[0]
    low = stock_prices.tail(1).iloc[0]
    return high, low

def get_cmpny_df(basic_info_csv: pd.DataFrame, cmpnyname: str):
    df = basic_info_csv.loc[basic_info_csv["Company_Name"] == cmpnyname]
    #If there is no data for the company
    if df["Operating_Income(added)_Profit_Status"].iloc[0] == np.nan:
        print("~" * 100)
        raise custom_exceptions.YoungCmpny
    return df