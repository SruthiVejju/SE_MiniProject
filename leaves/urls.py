from django.urls import path

from . import views

urlpatterns = [
    path('', views.my_requests, name='leave-mine'),
    path('new/', views.submit, name='leave-submit'),
    path('pending/', views.pending, name='leave-pending'),
    path('<int:pk>/decide/', views.decide, name='leave-decide'),
]
