import lib_one, custom_exceptions

import time

import FinanceDataReader as fdr
from tabulate import tabulate
from tqdm import tqdm
import pandas as pd
import pickle, os
import logging

def CreateSaveDF(cmpnyname: str, corp_code: str, year: str):
    sp_data = fdr.DataReader(corp_code, "2017-12-01", f"{year}-12-31") #GETTING A DATAFRAME OF THE STOCKPRICES OF THE CORP_CODE CORPORATION
    save_file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'Stocks', f"{cmpnyname}_stock.csv")
    sp_data.to_csv(save_file_path, encoding='euc-kr', index=False)

def main():
    #GETTING THE LIST OF NAMES AND THEIR CORPORATE CODES IN THE KOSPI FROM THE pkl object make with the modul in the Data directory
    file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl')
    with open(file_path, 'rb') as f:
        name_code = pickle.load(f)

    year = "2022"

    for key, val in tqdm(name_code.items()):
        CreateSaveDF(cmpnyname=key, corp_code=val, year=year)

if __name__ == "__main__":
    main()