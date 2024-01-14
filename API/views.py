from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .api_local import cmpny_data

import pickle, os

file_path = os.path.join(os.getcwd(), 'API', 'api_local', 'Data', 'name_code.pkl')

with open(file_path, 'rb') as f:
    name_code = pickle.load(f)

@api_view(['POST'])
def get_basic_info(request):
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]
    try:
        cmpnycode = name_code[cmpnyname]
    except KeyError:
        return Response({"error": "Bad Request: cmpnyname not in list"}, status=status.HTTP_400_BAD_REQUEST)
    
    print("~" * 100)
    print(cmpnyname)

    basic_info = cmpny_data.get_stock_info(cmpnycode)
    basic_info["cmpnyname"] = cmpnyname
    return Response(basic_info)