from .import lib_one

import FinanceDataReader as fdr
import pandas as pd

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

print(get_stock_info("005930"))