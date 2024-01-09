from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_cmpnyname(request):
    cmpnyname = {"cmpnyname":"삼성"}
    return Response(cmpnyname)