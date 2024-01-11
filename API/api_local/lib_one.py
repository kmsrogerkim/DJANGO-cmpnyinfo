from tabulate import tabulate
from datetime import date
import pandas as pd
import time

'''
11013: 1분기
11012: 반기
11014: 3분기
11011: 사업보고서
'''

class StockPriceError(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value
    
def Timer(func):
    def Wrapper(*args, **kwargs):
        print(func.__name__)
        start = time.time()
        obj = func(*args, **kwargs)
        end = time.time()
        print(end - start)
        print("-" * 20)
        return obj
    return Wrapper

def GetDateToday():
    today = date.today()
    x = today.weekday()
    today = pd.to_datetime(today)
    while x > 4:
        today -= pd.to_timedelta(1, 'D')
        x -= 1
    return today

def GetLastWeek(today: pd.Timestamp) -> pd.Timestamp:
    return (today - pd.to_timedelta(7, 'D'))

def GetFutureStockPrice(sp_data, date):
    '''
    Arguments: a dataframe object containing all the stock information of the company, the date
    Returns: the stock price closest in the future to the date given.
    '''
    #HAVE TO DO THIS CUZ THE sp_data returns Date as default index. So changing it back to column
    if sp_data.index[0] != 0: #IF THE INDEX OF THE DATA IS THE TIME, NOT 0,1,...
        sp_data.reset_index(inplace=True)  #SET TIME AS COLUMN AND REPLACE DEFAULT    
    
    date = pd.to_datetime(date)

    if sp_data['Date'].max() < date or sp_data['Date'].min() > date:
        #If the there isn't any stock value equivalent
        raise StockPriceError("Given date not in the dataframe 'sp_data'", date)
    else:
        while True:
            if sum(sp_data['Date'] == date) > 0:
                sp_data = sp_data[sp_data['Date'] == date]
                value = sp_data['Close'].iloc[0]
                break
            else:
                date += pd.to_timedelta(1, 'day')
        return value
    
def GetPastStockPrice(sp_data, date: str):
    '''
    Arguments: a dataframe object containing all the stock information of the company, the date
    Returns: the stock price closest from the past to the date given.
    '''

    #HAVE TO DO THIS CUZ THE sp_data returns Date as default index. So changing it back to column
    if sp_data.index[0] != 0: #IF THE INDEX OF THE DATA IS THE TIME, NOT 0,1,...
        sp_data.reset_index(inplace=True)  #SET TIME AS COLUMN AND REPLACE DEFAULT
    
    date = pd.to_datetime(date)

    if sp_data['Date'].max() < date or sp_data['Date'].min() > date:
        #If the there isn't any stock value equivalent
        raise StockPriceError("Given date not in the dataframe 'sp_data'", date)
    else:
        while True:
            if sum(sp_data['Date'] == date) > 0:
                sp_data = sp_data[sp_data['Date'] == date]
                value = sp_data['Close'].iloc[0]
                break
            else:
                date -= pd.to_timedelta(1, 'day')
        return value
    
def GetHLStockPrice(sp_data, date: str) -> dict:
    '''
    Arguments: a dataframe object containing all the stock information of the company, the date
    Returns: the high/low stock price closest from the past to the date given.
    '''

    #HAVE TO DO THIS CUZ THE sp_data returns Date as default index. So changing it back to column
    if sp_data.index[0] != 0: #IF THE INDEX OF THE DATA IS THE TIME, NOT 0,1,...
        sp_data.reset_index(inplace=True)  #SET TIME AS COLUMN AND REPLACE DEFAULT
    
    date = pd.to_datetime(date)
    value = {}

    if sp_data['Date'].max() < date or sp_data['Date'].min() > date:
        #If the there isn't any stock value equivalent
        raise StockPriceError("Given date not in the dataframe 'sp_data'", date)
    else:
        while True:
            if sum(sp_data['Date'] == date) > 0:
                sp_data = sp_data[sp_data['Date'] == date]
                value["Low"] = sp_data['Low'].iloc[0]
                value["High"] = sp_data['High'].iloc[0]
                break
            else:
                date -= pd.to_timedelta(1, 'day')
        return value