from django.urls import path
from . import views

urlpatterns = [
	path("basicInfo", views.get_basic_info),
	path("finstateSum", views.get_finstate_sum),
]