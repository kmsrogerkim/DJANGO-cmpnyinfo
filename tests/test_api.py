from rest_framework.test import APIRequestFactory #module for mocking requests
import pytest, json
import numpy as np

from API import views

class Request():
    def __init__(self, url: str, data: dict) -> None:
        self.factory = APIRequestFactory()
        self.request = self.factory.post(url, data)

def test_get_basic_info():
    request = Request("api/basicInfo/", {"cmpnyname" : "삼성전자"}).request
    #Action
    response = views.get_basic_info(request)
    response = response.data

    #Assert
    condition = (response["cmpnyname"] == "삼성전자" and len(list(response.keys())) == 6 and isinstance(response["Yesterday"], np.int64))
    assert condition == True

def test_fail_get_basic_info():
    '''
    The api must return 400 when the cmpnyname does not exist
    '''
    request = Request("api/basicInfo/", {"cmpnyname" : "김민승"}).request
    #Action
    response = views.get_basic_info(request)
    #Assert
    assert response.status_code == 400