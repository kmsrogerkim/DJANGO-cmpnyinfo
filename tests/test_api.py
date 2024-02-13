from django.test import TestCase
from rest_framework.test import APIRequestFactory #module for mocking requests

from API import views

class Request():
    def __init__(self, url: str, data: dict) -> None:
        self.factory = APIRequestFactory()
        # self.url = url
        # self.data = data
        self.request = self.factory.post(url, data)
class APITest(TestCase):
    def setUp(self):
        self.reqeust = Request("api/basicInfo/", {"cmpnyname" : "삼성전자"}).request

    def test_get_basic_info(self):
        views.get_basic_info(self.reqeust)