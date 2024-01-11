from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
	path("notfound", views.not_found, name="not_found"),
	# path("sign_up", views.sign_up, name="sign_up"),
	# path("sign_in", views.sign_in, name="sign_in"),
	path("cmpny/<str:cmpnyname>", views.cmpny, name="cmpny"),
]