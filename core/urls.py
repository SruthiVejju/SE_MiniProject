from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_student, name='register'),
    path('notifications/read/', views.mark_notifications_read, name='notifications-read'),
]