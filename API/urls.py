from django.urls import path
from . import views

urlpatterns = [
	path("basicInfo", views.get_basic_info),
]