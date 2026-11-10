from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.submit_complaint, name='complaint-submit'),
    path('', views.complaint_list, name='complaint-list'),
    path(
        '<int:pk>/update/',
        views.update_complaint,
        name='complaint-update'
    ),
]