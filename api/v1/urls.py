from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='v1-root'),
    path('health/', views.health_check, name='v1-health'),
    path('rooms/', views.rooms_api, name='v1-rooms'),
    path('notices/', views.notices_api, name='v1-notices'),
    path('notices/<int:pk>/', views.notice_detail_api, name='v1-notice-detail'),
    path('reports/occupancy/', views.occupancy_report_api, name='v1-occupancy-report'),
    path('complaints/', views.complaints_api, name='v1-complaints'),
    path('leaves/', views.leaves_api, name='v1-leaves'),
    path('fees/dues/', views.fees_dues_api, name='v1-fees-dues'),
]
