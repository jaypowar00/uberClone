from django.urls import path
from . import views

urlpatterns = [
    path('add-vehicle', views.add_vehicle),
    path('vehicle', views.vehicle_details),
    path('update-vehicle', views.update_vehicle),
    path('delete-vehicle', views.delete_vehicle),
    path('nearby', views.search_nearby_drivers),
]
