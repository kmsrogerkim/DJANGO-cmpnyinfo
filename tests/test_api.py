import pytest

from API import views

class Request():
    def __init__(self) -> None:
        self.data = {"cmpnyname" : "삼성전자"}

def test_get_basic_info():
    reqeust = Request()
    API.views.get_basic_info(reqeust)