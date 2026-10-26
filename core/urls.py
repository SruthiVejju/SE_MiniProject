from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('notifications/read/', views.mark_notifications_read, name='notifications-read'),
]
