from django.urls import path
from . import views

urlpatterns = [
	path("basicInfo/<str:cmpnyData>", views.get_basic_info),
	path("finstateSum/<str:cmpnyData>", views.get_finstate_sum),
	path("graphData/<str:cmpnyData>", views.get_graph_data),
    path("cmpnyList/<str:cmpnyData>", views.get_cmpny_list)
]