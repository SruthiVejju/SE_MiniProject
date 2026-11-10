from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.submit_complaint, name='complaint-submit'),
]