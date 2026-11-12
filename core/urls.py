
from django.urls import path

from . import views, auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path(
        'notifications/read/',
        views.mark_notifications_read,
        name='notifications-read'
    ),

    path(
        'register/',
        auth_views.register,
        name='register'
    ),

    path(
        'login/',
        auth_views.login_view,
        name='login'
    ),

    path(
        'logout/',
        auth_views.logout_view,
        name='logout'
    ),
]
