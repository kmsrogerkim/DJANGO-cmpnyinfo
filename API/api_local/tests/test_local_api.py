'''
Tests will be executed in root/API/api_local
Unlike every other file in api_local
'''
import pytest
import sys
sys.path.append('./')

from unittest.mock import patch

import create_basic_info as cbi
import create_bf_for_analysis as cbfa

from requests.exceptions import SSLError

from dotenv import load_dotenv
from tabulate import tabulate
import OpenDartReader
import pandas as pd
import pickle, os

load_dotenv()
dart_my_api = os.getenv("DART_API_KEY")

class Logger():
    def __init__(self) -> None:
        pass

    def error(*str):
        pass

#global vairble for df_BasicInfo
df_BasicInfo = None

class Test():
    def setup_method(self,method):
        print(f"Setting up {method}")

        my_api = dart_my_api #FROM THE API_KEYS FILE
        self.dart = OpenDartReader(my_api) #CREATING DART OBJECT 

        #GETTING THE FILE PATH RELATIVE TO THE ROOT DIR
        file_path = os.path.join(os.getcwd(), 'Data', 'name_code.pkl')

        #GETTING THE LIST OF NAMES AND THEIR CORPORATE CODES IN THE KOSPI FROM THE pkl object make with the modul in the Data directory
        with open(file_path, 'rb') as f:
            self.name_code = pickle.load(f)

        year = "2022"
        self.year_list = [(pd.to_datetime(year) - pd.DateOffset(years=3)).strftime('%Y')] + [year]
        #THIS LIST CONTAINS TWO ELEMENTS, THIS YEAR, AND THREE YEARS BEFORE IT.

        self.company_names = list(self.name_code.keys())
        self.invalid_company_names = ["김민승"]
        
        self.logger = Logger()

        self.BasicInfo = {
            'Company_Name':[],
            'Year':[],
            'Total_Assets' : [],
            'Total_Debt':[],
            'Total_Equity':[],
            'Revenue':[],
            'Operating_Income(added)': [],
            'Net_Income(added)':[],
            'Revenue_Increase_Rate':[],
            'Operating_Income(added)_Increase_Rate':[],
            'Net_Income(added)_Increase_Rate':[],
            'Revenue_Profit_Status':[],
            'Operating_Income(added)_Profit_Status':[],
            'Net_Income(added)_Profit_Status':[],
            'Debt_Equity_Ratio' : [],
            'ROA' : [],
            'ROE' : [],
            'EPS':[],
            'PER':[],
            'Stock_Num':[]
        }

    def test_cbi(self):
        #Excecuting
        cbi.RunLoop(self.BasicInfo, self.name_code, self.company_names, self.year_list, self.dart, self.logger)

        #Checking if the dict is legit  
        assert 606 == len(self.BasicInfo["Company_Name"]) and 20 == len(self.BasicInfo.keys())

        #Creating df_BasicInfo for cbfa
        global df_BasicInfo
        df_BasicInfo = pd.DataFrame(self.BasicInfo)

    def test_SSLError_cbi(self):
        with patch('create_basic_info.CreateCmpnyBF') as mock_get_b:
            mock_get_b.side_effect = SSLError
            
            cbi.RunLoop(self.BasicInfo, self.name_code, self.invalid_company_names, self.year_list, self.dart, self.logger)

    def test_cbfa(self):
        global df_BasicInfo
        years = list(df_BasicInfo["Year"][:6])
        stock_prices = pd.DataFrame({"Year":[], "Current_Stock":[], "Future_Stock":[]})

        cbfa.RunLoop(self.company_names, self.name_code, years, stock_prices, self.logger)
        cbfa.Append(df_BasicInfo, stock_prices)