from django.urls import path, include
from . import views

urlpatterns = [
    path('locations', views.get_trip_locations),
    path('get-location-path', views.get_location_path),
]
