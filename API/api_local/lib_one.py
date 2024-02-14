from tabulate import tabulate
from datetime import date
import pandas as pd
import time, os, sys

try:
    from . import custom_exceptions #When running as django
except Exception as e:
    import custom_exceptions #When running as api_local

'''
11013: 1분기
11012: 반기
11014: 3분기
11011: 사업보고서
'''
    
def timer(func):
    def Wrapper(*args, **kwargs):
        print(func.__name__)
        start = time.time()
        obj = func(*args, **kwargs)
        end = time.time()
        print(end - start)
        print("-" * 20)
        return obj
    return Wrapper

def get_date_today():
    today = date.today()
    x = today.weekday()
    today = pd.to_datetime(today)
    while x > 4:
        today -= pd.to_timedelta(1, 'D')
        x -= 1
    return today

def get_last_week(today: pd.Timestamp) -> pd.Timestamp:
    return (today - pd.to_timedelta(7, 'D'))

def get_six_years_list(year: str) -> list:
    '''
    Returns: List of strings, past six yrs.
    '''
    year = int(year)
    year_list = []
    for i in range(year-5, year+1):
        year_list.append(str(i))
    return year_list

def get_stock_price(sp_data, date: str) -> dict:
    '''
    Arguments: a dataframe object containing all the stock information of the company; the date
    Returns: the high/low/close stock price closest from the past to the date given.
    '''
    date = pd.to_datetime(date)

    #HAVE TO DO THIS CUZ THE sp_data returns Date as default index. So changing it back to column
    if sp_data.index[0] != 0: #IF THE INDEX OF THE DATA IS THE TIME, NOT 0,1,...
        sp_data.reset_index(inplace=True)  #SET TIME AS COLUMN AND REPLACE DEFAULT

    #If the latest stock price is not within one week range
    no_new_data = (date - sp_data["Date"].max()) > pd.Timedelta(days=7)

    if no_new_data or sp_data['Date'].min() > date:
        #If the there isn't any stock value equivalent
        raise custom_exceptions.StockPriceError("Given date not in the dataframe 'sp_data'", date)
    else:
        value = {}
        while True:
            if sum(sp_data['Date'] == date) > 0:
                sp_data = sp_data[sp_data['Date'] == date]
                value["Low"] = sp_data['Low'].iloc[0]
                value["High"] = sp_data['High'].iloc[0]
                value["Close"] = sp_data['Close'].iloc[0]
                break
            else:
                date -= pd.to_timedelta(1, 'day')
        return value

def get_cmpny_stock(cmpnyname: str):
    try:
        file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'Stocks', f"{cmpnyname}_stock.csv")
        df = pd.read_csv(file_path, encoding="euc-kr", parse_dates=["Date"])
    except FileNotFoundError:
        raise custom_exceptions.YoungCmpny(corp_code=cmpnyname, end_year="2022") #When the Stock doesn't match
    except:
        file_path = os.path.join(os.getcwd(), 'Data', 'Stocks', f"{cmpnyname}_stock.csv") #When testing
        df = pd.read_csv(file_path, encoding="euc-kr", parse_dates=["Date"])
    return df

def display_timer(t: int):
    '''
    Prints out the timer into the terminal
    '''
    print("\nTimer Starting:")
    for i in range(t,0,-1):
        sys.stdout.write(str(i)+' ')
        sys.stdout.flush()
        time.sleep(1)

def reattempt_until_failure(max_attempt: int, time: int):
    '''
    An decorator function
    Waits for 30 seconds when the function fails.
    '''
    def reattempt_until_failure_function(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts != max_attempt:
                if attempts == max_attempt:
                    raise custom_exceptions.ReAttemptFail(max_attempt)
                try:
                    data = func(*args, **kwargs)
                except custom_exceptions.ResponseError as e:
                    if e.status_code == 413:
                        raise custom_exceptions.ReAttemptFail(max_attempt) #IF THE ERROR CODE IS 413, it means a special case where the request in invalid. So for now, just skip it.
                    print(f"{e.messaage}\nRetrying: {attempts} attempts / {max_attempt} max attempts")
                    display_timer(time)
                    attempts += 1
                    continue
                except Exception as e:
                    print(f"{e}\nRetrying: {attempts} attempts / {max_attempt} max attempts")
                    display_timer(time)
                    attempts += 1
                    continue
                break
            return data
        return wrapper
    return reattempt_until_failure_function