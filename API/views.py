from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def get_basic_info(request):
    post_data = request.data #dict
    cmpnyname = post_data["cmpnyname"]
    
    cmpnyname = {"cmpnyname":cmpnyname}
    return Response(cmpnyname)