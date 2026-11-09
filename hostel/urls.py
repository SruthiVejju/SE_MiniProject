
from django.urls import path
from . import views

app_name = "hostel"

urlpatterns = [
    path("rooms/", views.room_list, name="room_list"),
    path("allocate/", views.allocate_room, name="allocate"),
    path(
        "allocation/<int:pk>/success/",
        views.allocation_success,
        name="allocation_success"
    ),
]
