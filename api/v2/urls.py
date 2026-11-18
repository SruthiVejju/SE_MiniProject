from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root_v2, name='v2-root'),
    path('rooms/', views.rooms_api_v2, name='v2-rooms'),
    path('notices/', views.notices_api_v2, name='v2-notices'),
    path('reports/occupancy/', views.occupancy_report_api_v2, name='v2-occupancy-report'),
]
