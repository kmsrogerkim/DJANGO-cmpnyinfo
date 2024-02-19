from rest_framework.test import APIRequestFactory #module for mocking requests
import pytest, json
import numpy as np
import pprint

from API import views

class Request():
    def __init__(self, url: str, data: dict) -> None:
        self.factory = APIRequestFactory()
        self.request = self.factory.post(url, data)

class TestByCmpnyName():
    def setup_method(self, method):
        print(f"Setting up {method}")
        self.good_request_data = {"cmpnyname" : "삼성전자"}
        self.young_request_data = {"cmpnyname" : "삼성전자우"}
        self.not_found_request_data = {"cmpnyname" : "김민승"}

    def test_get_basic_info(self):
        request = Request("api/basicInfo/", self.good_request_data).request

        response = views.get_basic_info(request)
        response = response.data

        assert response["cmpnyname"] == "삼성전자" and len(list(response.keys())) == 7 and isinstance(response["Yesterday"], np.int64)

    def test_fail_get_basic_info(self):
        '''
        The api must return 404 when the cmpnyname does not exist
        '''
        request = Request("api/basicInfo/", self.not_found_request_data).request
        response = views.get_basic_info(request)
        assert response.status_code == 404

    def test_get_finstate_sum(self):
        request = Request("api/finstateSum/", self.good_request_data).request

        response = views.get_finstate_sum(request)
        response = response.data

        assert len(response) == 6 and len(response[0].keys()) == 16

    def test_fail_get_finstate_sum(self):
        request = Request("api/finstateSum/", self.young_request_data).request
        response = views.get_finstate_sum(request)
        assert response.status_code == 400

    def test_get_graph_data(self):
        request = Request("api/graphData/", self.good_request_data).request

        response = views.get_graph_data(request)
        response = response.data

        assert len(response.keys()) == 3

    def test_fail_get_graph_data(self):
        request = Request("api/graphData/", self.young_request_data).request
        response = views.get_graph_data(request)
        assert response.status_code == 400

class TestByCorpCode(TestByCmpnyName):
    def setup_method(self, method):
        print(f"Setting up {method}")
        self.good_request_data = {"cmpnyname" : "005930"}
        self.young_request_data = {"cmpnyname" : "005935"}
        self.not_found_request_data = {"cmpnyname" : "0"}