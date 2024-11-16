'''
GETTING THE LIST OF NAMES AND THEIR CORPORATE CODES IN THE KOSPI
'''
import FinanceDataReader as fdr
import pickle, os

KOP_list = fdr.StockListing('KOSPI')
KOP_list = KOP_list.loc[0:100, ['Code', 'Name']]
name_code = dict(zip(KOP_list['Name'], KOP_list['Code']))

#GETTING THE FILE PATH RELATIVE TO THE ROOT DIR
file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl')

with open(file_path, 'wb') as f:
    pickle.dump(name_code, f)