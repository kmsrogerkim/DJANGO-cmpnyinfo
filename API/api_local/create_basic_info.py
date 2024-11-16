import lib_one, custom_exceptions

from requests.exceptions import SSLError

import FinanceDataReader as fdr
from tabulate import tabulate
import OpenDartReader
from tqdm import tqdm
import pandas as pd
import numpy as np
import pickle, os
import time, logging 

dart_my_api = os.getenv("DART_API_KEY")

def GetIncreaseRate(BasicInfo):
    '''
    Arguments: the BasicInfor dict
    Returns: NOTHING. Only modifies the dict and completes the Increase_Rate columns
    '''
    triger = False
    start_index = len(BasicInfo["Company_Name"]) - 6
    for key in BasicInfo:
        if key == "Revenue_Increase_Rate" or triger:
            triger = True
            BasicInfo[key].append(0)
            for i in range(1, 6):
                #CALCULATE THE DATA, EXCEPT FOR THE INITIAL ONE
                current_value = BasicInfo[key.replace("_Increase_Rate", '')][start_index+i]
                past_value = BasicInfo[key.replace("_Increase_Rate", '')][start_index+i-1]
                increase_rate = (((current_value - past_value) / current_value) * 100)
                BasicInfo[key].append(round(increase_rate, 2))
        if key == "Net_Income(added)_Increase_Rate":
            break

def GetProfitStatus(BasicInfo: dict):
    '''
    Arguments: the BasicInfor dict
    Returns: NOTHING. Only modifies the dict and completes the Profit Status columns
    '''
    start_index = len(BasicInfo["Revenue_Profit_Status"])
    triger = False
    for keys in BasicInfo:
        if keys == "Revenue_Profit_Status" or triger:
            triger = True
            #Initializing status for the first year.
            if BasicInfo[keys.replace("_Profit_Status", '')][start_index] > 0:
                status = "P"
            else:
                status = "L"
            BasicInfo[keys].append(status)

            #Finishing the other five years
            for i in range(start_index + 1, start_index + 6):
                if BasicInfo[keys.replace("_Profit_Status", '')][i] > 0:
                    status = "P"
                    if BasicInfo[keys.replace("_Profit_Status", '')][i-1] > 0:
                        status += "_Contd"
                    else:
                        status += "_Turned"
                else:
                    status = "L"
                    if BasicInfo[keys.replace("_Profit_Status", '')][i-1] < 0:
                        status += "_Contd"
                    else:
                        status += "_Turned"
                BasicInfo[keys].append(status)
        if keys == "Net_Income(added)_Profit_Status":
            break

@lib_one.timer
def GetNumbers(finstate, BasicInfo: dict) -> dict:
    '''
    Arguments: a dart finstate API object, BasicInfo dict
    Returns: NOTHING. Only modifies the dict object which is mutable. GETS ALL THE VALUE FROM Total_Assets to Net_Income(added)
    '''
    #CREATING LISTS TO GET DATA OF EACH OF THE FOLLOWING CRITERIAS
    k_keyword_list = ["자산총계", "부채총계", "자본총계", "매출액", "영업이익", "당기순이익"]
    e_keyword_list = [items for items in BasicInfo.keys()][2:8] 
    #GETTING EACH DATA AND APPENDING TO THE BASICINFO DICT
    for i in range(6):
        temp = finstate.loc[(finstate["account_nm"] == k_keyword_list[i]) & (finstate["fs_nm"] == '재무제표')] 
        if temp.empty:
            BasicInfo[e_keyword_list[i]] += [np.nan]*3
        else:
            temp_number = temp[['bfefrmtrm_amount', 'frmtrm_amount', 'thstrm_amount']]
            for col_name, col_item in temp_number.items():
                BasicInfo[e_keyword_list[i]].append(col_item.str.replace(",","").astype(float).values[0])

def GetRatios(BasicInfo):
    '''
    Arguments: a dart finstate API object, BasicInfo dict
    Returns: NOTHING. Modifies the dict object to add DER, ROA, and ROE
    '''
    for i in range(6):
        BasicInfo["Debt_Equity_Ratio"].append(round(100 * BasicInfo["Total_Debt"][i] / BasicInfo['Total_Equity'][i], 2))
        BasicInfo["ROA"].append(round(100 * BasicInfo["Net_Income(added)"][i] / BasicInfo['Total_Assets'][i], 2))
        BasicInfo["ROE"].append(round(100 * BasicInfo["Net_Income(added)"][i] / BasicInfo['Total_Equity'][i], 2))

def GetFinState(dart, BasicInfo, corp_code: str, year: str) -> dict:
    '''
    Arguments: OpenDartReader API object, BasicInfo, corp_code, the year.
    Returns, a dictionary object containing all the objects.
    '''
    try:
        finstate = dart.finstate(corp_code, year, "11011") #RETURNS A DATAFRAME OBJECT THAT IS THE FINANCIAL STATEMENT OF THE COMPAN; BECAUSE OF "11011", IT RETURNS 사업보고서
    except:
        #If the company is younger than 6 years
        raise custom_exceptions.YoungCmpny(corp_code=corp_code, end_year=year)
        
    GetNumbers(finstate, BasicInfo) #GETS ALL THE VALUE FROM Total_Assets to Net_Income(added)

    return BasicInfo

def GetStockNum(dart, corp_code: str, year: int) -> int:
    '''
    Returns: The total number of stock in the market in the given year.
    '''
    try:
        report = dart.report(corp_code, "주식총수", year, "11011")
        report = report.loc[(report["se"] == "합계"), "istc_totqy"]
        stock_num = report.str.replace(",","").astype(int).values[0]
    except (ValueError, KeyError):
        raise custom_exceptions.YoungCmpny(corp_code, year)
    return stock_num

def GetReport(dart, corp_code: str, cmpnyname: str, year: int) -> dict:
    '''
    Arguments: OpenDartReader API object, corp_code, year
    Returns: dictionary obj of key_info containing the EPS and the PER of the year, and two years prior to that.
    '''
    key_info = {
        'EPS': [],
        'PER': [],
    }
    report = dart.report(corp_code, "배당", year, "11011") #GETTING THE STATEMENT OF PROFIT OR LOSS
    sp_data = lib_one.get_cmpny_stock(cmpnyname) #GETTING A DATAFRAME OF THE STOCKPRICES OF THE CORP_CODE CORPORATION

    #GETTING THE EPS FROM THE STATEMENT OF PROFIT OR LOSS
    EPS = report[(report['se'].str.contains('주당순이익'))]

    #APPENDING THE EPS FROM EACH YEAR AS FLOAT OBJECT TO THE DICT
    e_keyword_list = ['lwfr', 'frmtrm', 'thstrm']
    for i in range(3):
        key_info['EPS'].append(EPS[e_keyword_list[i]].str.replace(",","").astype(float).values[0])

    #TRANSFORMS DATE INTO TWO YEARS AGO FROM THE GIVEN TIME.
    date = str(year) + "-12-31"
    date = pd.to_datetime(date)
    date -= pd.DateOffset(years=2)

    #GETTING THE PER OF EACH YEAR, DATE = 12.31; 당기 마지막 주가 기준 PER 계산
    for i in range(3):
        key_info['PER'].append(round(lib_one.get_stock_price(sp_data, date.strftime('%Y-%m-%d'))["Close"] / key_info['EPS'][i], 2))
        date += pd.DateOffset(years=1)

    return key_info

def CreateCmpnyBF(BasicInfo: dict, name_code: dict, company_name: str, year_list: list, dart, logger):
    '''
    Returns: Nothing. Modifies BasicInfo for each compnay
    '''
    BasicInfo['Company_Name'] += [company_name] * 6
    BasicInfo["Year"] += lib_one.get_six_years_list(year=year_list[1])

    try:
        stock_num = GetStockNum(dart, name_code[company_name], year_list[1])
        stock_num = [np.nan] * 5 + [stock_num]
        BasicInfo["Stock_Num"] += stock_num
        for years in year_list:
            #HAS TO RUN TWICE BECAUSE EACH API CAN ONLY CALL DATA FROM UP TO 3 YEARS AGO
            GetFinState(dart, BasicInfo, name_code[company_name], year=years)
            finReport = GetReport(dart, corp_code=name_code[company_name], cmpnyname=company_name, year=years)
            BasicInfo['EPS'] += finReport['EPS']
            BasicInfo['PER'] += finReport['PER']
    except (custom_exceptions.StockPriceError, custom_exceptions.YoungCmpny) as e:
        logger.error(f"{e}")
        start_index = len(BasicInfo["Company_Name"])-6
        for key, value in BasicInfo.items():
            if key != "Company_Name" and key != "Year":
                BasicInfo[key][start_index:start_index+6] = [np.nan] * 6
        return 0

    #COMPLETING THE BasicInfo DICT FOR THOSE DATA THAT CAN BE RAN 6 TIMES
    GetIncreaseRate(BasicInfo)
    GetRatios(BasicInfo)
    GetProfitStatus(BasicInfo)

def AdjustLen(BasicInfo: dict):
    '''
    Adjust everything in BasicInfo to before the iteration.
    '''
    length = (len(BasicInfo["Company_Name"]) - 6)
    for key, val in BasicInfo.items():
        BasicInfo[key] = val[:length]
    return BasicInfo

def RunLoop(BasicInfo: dict, name_code: dict, company_names: list, year_list: list, dart, logger):
    '''
    Arguments: all the initialized data
    Returns: nothing. Just runs the loop and handles exceptions
    '''
    for i in tqdm(range(len(company_names))):
        try:
            for key, value in BasicInfo.items():
                if (len(value)) != len(BasicInfo["Company_Name"]):
                    print("a")
            CreateCmpnyBF(BasicInfo, name_code, company_names[i], year_list, dart, logger)
        except SSLError as e:
            #When I give too much request to dart
            logger.error(f"{e}")
            for j in range(1, 5):
                BasicInfo = AdjustLen(BasicInfo)
                time.sleep(j)
                try:
                    CreateCmpnyBF(BasicInfo, name_code, company_names[i], year_list, dart, logger)
                    break
                except Exception as e:
                    logger.error(f"{e}")
                    if j == 4:
                        start_index = len(BasicInfo["Company_Name"]) - 6
                        for key, value in BasicInfo.items():
                            if key != "Company_Name" and key != "Year":
                                value[start_index:start_index+6] = [np.nan] * 6
                    continue

def main():
    my_api = dart_my_api #FROM THE API_KEYS FILE
    dart = OpenDartReader(my_api) #CREATING DART OBJECT 

    #GETTING THE FILE PATH RELATIVE TO THE ROOT DIR
    file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl')

    #GETTING THE LIST OF NAMES AND THEIR CORPORATE CODES IN THE KOSPI FROM THE pkl object make with the modul in the Data directory
    with open(file_path, 'rb') as f:
        name_code = pickle.load(f)

    year = "2022"
    year_list = [(pd.to_datetime(year) - pd.DateOffset(years=3)).strftime('%Y')] + [year]
    #THIS LIST CONTAINS TWO ELEMENTS, THIS YEAR, AND THREE YEARS BEFORE IT.

    BasicInfo = {
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

    #For logging
    logging.basicConfig(filename="./API/api_local/logs/create_basic_info.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()

    company_names = list(name_code.keys())
    RunLoop(BasicInfo, name_code, company_names, year_list, dart, logger)

    #CREATING FILE PATH FOR SAVING THE CSV TABLE    
    save_file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'basic_info.csv')

    #CONVERTING IT TO DF THEN SAVING IT
    BasicInfo = pd.DataFrame(BasicInfo)
    BasicInfo.to_csv(save_file_path, encoding='euc-kr', index=False)

if __name__ == "__main__":
    main()