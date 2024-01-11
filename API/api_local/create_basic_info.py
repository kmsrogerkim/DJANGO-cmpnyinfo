#THIS 'API_KEYS' IS A PYTHON FILE OF MINE THAT SOTERS MY PRIVATE API KEYS.
from API_KEYS import * #SO DELETE THIS LINE!!!!!

import lib_one

import FinanceDataReader as fdr
from tabulate import tabulate
import OpenDartReader
import pandas as pd
import pickle

def GetIncreaseRate(BasicInfo):
    '''
    Arguments: the BasicInfor dict
    Returns: NOTHING. Only modifies the dict and completes the Increase_Rate columns
    '''
    triger = False
    for key in BasicInfo:
        if key == "Revenue_Increase_Rate" or triger:
            #WHEN THE ITERATION REACHES THE Revenue_Increase_Rate
            triger = True
            BasicInfo[key].append(0)
            for i in range(1, 6):
                #CALCULATE THE DATA, EXCEPT FOR THE INITIAL ONE
                BasicInfo[key].append(((BasicInfo[key.replace("_Increase_Rate", '')][i] - BasicInfo[key.replace("_Increase_Rate", '')][i-1]) / BasicInfo[key.replace("_Increase_Rate", '')][i]) * 100)
        if key == "Net_Income(added)_Increase_Rate":
            break

def GetProfitStatus(BasicInfo):
    '''
    Arguments: the BasicInfor dict
    Returns: NOTHING. Only modifies the dict and completes the Profit Status columns
    '''
    triger = False
    for keys in BasicInfo:
        if keys == "Revenue_Profit_Status" or triger:
            triger = True
            if BasicInfo[keys.replace("_Profit_Status", '')][0] > 0:
                status = "P"
            else:
                status = "L"
            BasicInfo[keys].append(status)
            for i in range(1, 6):
                if BasicInfo[keys.replace("_Profit_Status", '')][i] > 0:
                    status = "P"
                    if BasicInfo[keys.replace("_Profit_Status", '')][i-1] > 0:
                        status += "_Contd"
                    else:
                        status += "_Turned"
                else:
                    status = "L"
                    if BasicInfo[keys.replace("_Profit_Status", '')][i-1] > 0:
                        status += "_Contd"
                    else:
                        status += "_Turned"
                BasicInfo[keys].append(status)
            if keys == "Net_Income(added)_Profit_Status":
                break

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

@lib_one.Timer
def GetFinState(dart, BasicInfo, corp_code: str, year: int) -> dict:
    '''
    Arguments: OpenDartReader API object, BasicInfo, corp_code, the year.
    Returns, a dictionary object containing all the objects.
    '''
    finstate = dart.finstate(corp_code, year, "11011") #RETURNS A DATAFRAME OBJECT THAT IS THE FINANCIAL STATEMENT OF THE COMPAN; BECAUSE OF "11011", IT RETURNS 사업보고서

    #GETTING THE YEARS
    temp = finstate.loc[(finstate["account_nm"] == "자산총계") & (finstate["fs_nm"] == '재무제표')]
    temp_date = temp[["bfefrmtrm_dt", 'frmtrm_dt', 'thstrm_dt']] #당기, 전기, 전전기
    for col_name, col_item in temp_date.items():
        BasicInfo["Year"].append(str(col_item)[6:10]) #GETTING ONLY THE '2022' PART FROM THE ENTIRE DATE
    
    GetNumbers(finstate, BasicInfo) #GETS ALL THE VALUE FROM Total_Assets to Net_Income(added)

    return BasicInfo

@lib_one.Timer
def GetReport(dart, corp_code: str, year: int) -> dict:
    '''
    Arguments: OpenDartReader API object, corp_code, year
    Returns: dictionary obj of key_info containing the EPS and the PER of the year, and two years prior to that.
    '''
    key_info = {
        'EPS': [],
        'PER': [],
    }
    report = dart.report(corp_code, "배당", year, "11011") #GETTING THE STATEMENT OF PROFIT OR LOSS
    today = lib_one.GetDateToday()
    sp_data = fdr.DataReader(corp_code, "2017-12-01", today) #GETTING A DATAFRAME OF THE STOCKPRICES OF THE CORP_CODE CORPORATION

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
        key_info['PER'].append(round(lib_one.GetPastStockPrice(sp_data, date.strftime('%Y-%m-%d')) / key_info['EPS'][i], 2))
        date += pd.DateOffset(years=1)

    return key_info

@lib_one.Timer
def main():
    my_api = dart_my_api
    dart = OpenDartReader(my_api) #CREATING DART OBJECT 

    #GETTING THE LIST OF NAMES AND THEIR CORPORATE CODES IN THE KOSPI FROM THE pkl object make with the modul in the Data directory
    with open('../Invest/Data/name_code.pkl', 'rb') as f:
        name_code = pickle.load(f)

    company_name = "삼성전자"

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
        'PER':[]
    }

    BasicInfo['Company_Name'] += [company_name] * 6
    for years in year_list:
        #HAS TO RUN TWICE BECAUSE EACH API CAN ONLY CALL DATA FROM UP TO 3 YEARS AGO
        GetFinState(dart, BasicInfo, name_code[company_name], year=years)

        finReport = GetReport(dart, name_code[company_name], years)
        BasicInfo['EPS'] += finReport['EPS']
        BasicInfo['PER'] += finReport['PER']

    #COMPLETING THE BasicInfo DICT FOR THOSE DATA THAT CAN BE RAN 6 TIMES
    GetIncreaseRate(BasicInfo)
    GetRatios(BasicInfo)
    GetProfitStatus(BasicInfo)

    #CONVERTING IT TO DF THEN SAVING IT
    BasicInfo = pd.DataFrame(BasicInfo)
    BasicInfo.to_csv(f"../Invest/Data/{company_name}_basic_info.csv", encoding='euc-kr', index=False)

if __name__ == "__main__":
    main()