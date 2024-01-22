import lib_one

import FinanceDataReader as fdr
from tabulate import tabulate
from tqdm import tqdm
import pandas as pd
import numpy as np
import pickle, os

def GetStockPrices(sp_data: pd.DataFrame, years: list) -> pd.DataFrame:
    '''
    Arguments: sp_data containing all the stock data, list of years.
    Returns: a dataframe that contains two columns of 'Current_Stock' and 'Future_Stock'
    '''
    dict_stock_data = {
        "Year": years,
        "Current_Stock":[],
        "Future_Stock":[]
    }

    year_date = str(years[0]) + "-12-31"
    curr_stock = lib_one.GetPastStockPrice(sp_data, year_date)
    dict_stock_data["Current_Stock"].append(curr_stock)

    for i in range(1,6):
        year_date = str(years[i]) + "-12-31"
        curr_stock = lib_one.GetPastStockPrice(sp_data, year_date)
        dict_stock_data["Future_Stock"].append(curr_stock)
        dict_stock_data["Current_Stock"].append(curr_stock) 
    dict_stock_data["Future_Stock"].append(0) #The last 'Future_Stock' is zero, cuz it's the newest.

    return pd.DataFrame(dict_stock_data)
    
def main():
    #GETTING THE FILE PATH RELATIVE TO THE ROOT DIR
    file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl')

    with open(file_path, 'rb') as f:
        name_code = pickle.load(f)

    file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'basic_info.csv')
    BasicInfo = pd.read_csv(file_path, encoding="euc-kr")
    BasicInfo.drop(['Total_Assets', 'Total_Debt', 'Total_Equity', 'Revenue', 'Operating_Income(added)', 'Net_Income(added)',], axis=1, inplace=True) #DELETING DATA THAT'S NOT GONNA BE USED

    company_names = list(name_code.keys())
    years = list(BasicInfo["Year"][:6])
    stock_prices = pd.DataFrame({"Year":[], "Current_Stock":[], "Future_Stock":[]})

    for i in tqdm(range(len(company_names))):
        company_name = company_names[i]
        try:
            sp_data = fdr.DataReader(name_code[company_name], "2017-12-01", lib_one.GetDateToday()) #GETTING A DATAFRAME OF THE STOCKPRICES OF THE CORP_CODE CORPORATION
            temp_stock_prices = GetStockPrices(sp_data, years)
        except Exception as e:
            print(e)
            temp_stock_prices = pd.DataFrame({"Year":[np.nan]*6, "Current_Stock":[np.nan]*6, "Future_Stock":[np.nan]*6})
            stock_prices = pd.concat([stock_prices, temp_stock_prices], ignore_index=True)
            continue
        stock_prices = pd.concat([stock_prices, temp_stock_prices], ignore_index=True)

    # BasicInfo = pd.merge(left=BasicInfo, right=stock_prices, on="Year", how="outer") #ADDING THE STOCKPRICES DF TO THE BASICINFO DF
    columns = list(BasicInfo.columns) + list(stock_prices.columns)[1:]
    BasicInfo = pd.concat([BasicInfo, stock_prices], axis=1, ignore_index=True) #ADDING THE STOCKPRICES DF TO THE BASICINFO DF
    BasicInfo.drop(BasicInfo.columns[13], axis=1, inplace=True)
    BasicInfo.columns = columns

    #SAVING IT
    file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'basic_info_for_analysis.csv')
    BasicInfo.to_csv(file_path, encoding='euc-kr', index=False)

if __name__ == "__main__":
    main()