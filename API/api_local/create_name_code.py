'''
GETTING THE LIST OF NAMES AND THEIR CORPORATE CODES IN THE KOSPI
'''
import FinanceDataReader as fdr
import pickle 

KOP_list = fdr.StockListing('KOSPI')
KOP_list = KOP_list.loc[0:100, ['Code', 'Name']]
name_code = dict(zip(KOP_list['Name'], KOP_list['Code']))

with open('../Invest/Data/name_code.pkl', 'wb') as f:
    pickle.dump(name_code, f)