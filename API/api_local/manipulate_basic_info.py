import FinanceDataReader as fdr
from tabulate import tabulate
import pandas as pd
import lib_one
import pickle

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
    with open('../Invest/Data/name_code.pkl', 'rb') as f:
        name_code = pickle.load(f)

    company_name = "삼성전자"

    BasicInfo = pd.read_csv(f"../Invest/Data/{company_name}_basic_info.csv", encoding="euc-kr")
    BasicInfo.drop(['Total_Assets', 'Total_Debt', 'Total_Equity', 'Revenue', 'Operating_Income(added)', 'Net_Income(added)',], axis=1, inplace=True) #DELETING DATA THAT'S NOT GONNA BE USED

    sp_data = fdr.DataReader(name_code[company_name], "2017-12-01", lib_one.GetDateToday()) #GETTING A DATAFRAME OF THE STOCKPRICES OF THE CORP_CODE CORPORATION

    years = list(BasicInfo["Year"])

    stock_prices = GetStockPrices(sp_data, years)

    BasicInfo = pd.merge(left=BasicInfo, right=stock_prices, on="Year", how="outer") #ADDING THE STOCKPRICES DF TO THE BASICINFO DF

    #SAVING IT
    BasicInfo.to_csv(f"../Invest/Data/{company_name}_basic_info_for_analysis.csv", encoding='euc-kr', index=False)

if __name__ == "__main__":
    main()