from rest_framework.response import Response
from rest_framework.decorators import api_view

from .api_local import cmpny_data

import pickle, os

file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl')

with open(file_path, 'rb') as f:
    name_code = pickle.load(f)

@api_view(['POST'])
def get_basic_info(request):
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]
    cmpnycode = name_code[cmpnyname]
    print("~" * 100)
    print(cmpnyname)

    basic_info = cmpny_data.get_stock_info(cmpnycode)
    print("=" * 100)
    print(basic_info)
    print("=" * 100)

    cmpnyname = {"cmpnyname":cmpnyname}
    return Response(cmpnyname)