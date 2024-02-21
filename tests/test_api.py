from rest_framework.test import APIRequestFactory #module for mocking requests
import numpy as np
import pytest

from API import views

class Request():
    def __init__(self, url: str) -> None:
        self.factory = APIRequestFactory()
        self.request = self.factory.get(url)

class TestByCmpnyName():
    def setup_method(self, method):
        print(f"Setting up {method}")
        self.good_cmpnyData = "삼성전자"
        self.young_cmpnyData = "삼성전자우"
        self.not_found_cmpnyData = "김민승"

    def test_get_basic_info(self):
        request = Request("api/basicInfo").request

        response = views.get_basic_info(request, self.good_cmpnyData)
        response = response.data

        assert response["cmpnyname"] == "삼성전자" and len(list(response.keys())) == 7 and isinstance(response["Yesterday"], np.int64)

    def test_fail_get_basic_info(self):
        '''
        The api must return 404 when the cmpnyname does not exist
        '''
        request = Request("api/basicInfo").request
        response = views.get_basic_info(request, self.not_found_cmpnyData)
        assert response.status_code == 404

    def test_get_finstate_sum(self):
        request = Request("api/finstateSum").request

        response = views.get_finstate_sum(request, self.good_cmpnyData)
        response = response.data

        assert len(response) == 6 and len(response[0].keys()) == 16

    def test_fail_get_finstate_sum(self):
        request = Request("api/finstateSum").request
        response = views.get_finstate_sum(request, self.young_cmpnyData)
        assert response.status_code == 400

    def test_get_graph_data(self):
        request = Request("api/graphData/").request

        response = views.get_graph_data(request, self.good_cmpnyData)
        response = response.data

        assert len(response.keys()) == 3

    def test_fail_get_graph_data(self):
        request = Request("api/graphData").request
        response = views.get_graph_data(request, self.young_cmpnyData)
        assert response.status_code == 400

class TestByCorpCode(TestByCmpnyName):
    def setup_method(self, method):
        print(f"Setting up {method}")
        self.good_cmpnyData = "005930"
        self.young_cmpnyData = "005935"
        self.not_found_cmpnyData = "0"