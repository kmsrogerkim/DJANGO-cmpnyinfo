from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
	path("notfound", views.not_found, name="not_found"),
    path("about", views.about, name="about"),
	path("cmpny/<str:cmpnyname>", views.cmpny, name="cmpny"),
]