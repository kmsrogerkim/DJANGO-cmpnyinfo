from django.urls import path
from . import views

urlpatterns = [
	path("cmpnyname", views.get_cmpnyname),
]