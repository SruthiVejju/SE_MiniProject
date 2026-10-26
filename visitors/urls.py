from django.urls import path

from . import views

urlpatterns = [
    path('', views.visitor_list, name='visitor-list'),
    path('entry/', views.log_entry, name='visitor-entry'),
    path('<int:pk>/exit/', views.log_exit, name='visitor-exit'),
]
