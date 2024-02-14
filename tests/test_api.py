from rest_framework.test import APIRequestFactory #module for mocking requests
import pytest, json
import numpy as np

from API import views

class Request():
    def __init__(self, url: str, data: dict) -> None:
        self.factory = APIRequestFactory()
        self.request = self.factory.post(url, data)

# @pytest.mark.skip
def test_get_basic_info():
    request = Request("api/basicInfo/", {"cmpnyname" : "삼성전자"}).request

    response = views.get_basic_info(request)
    response = response.data

    assert response["cmpnyname"] == "삼성전자" and len(list(response.keys())) == 6 and isinstance(response["Yesterday"], np.int64)

# @pytest.mark.skip
def test_fail_get_basic_info():
    '''
    The api must return 400 when the cmpnyname does not exist
    '''
    request = Request("api/basicInfo/", {"cmpnyname" : "김민승"}).request
    response = views.get_basic_info(request)
    assert response.status_code == 400

def test_get_finstate_sum():
    request = Request("api/finstateSum/", {"cmpnyname" : "삼성전자"}).request

    response = views.get_finstate_sum(request)
    response = response.data

    assert len(response) == 6 and len(response[0].keys()) == 16

def test_fail_get_finstate_sum():
    request = Request("api/finstateSum/", {"cmpnyname" : "삼성전자우"}).request
    response = views.get_finstate_sum(request)
    assert response.status_code == 400