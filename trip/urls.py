from django.urls import path, include
from . import views

urlpatterns = [
    path('get-trip-price', views.get_trip_price),
    path('book', views.book_trip),
    path('history', views.get_trip_history),
    path('payment/pay', views.pay_trip),
    path('locations', views.get_trip_locations),
    path('get-location-path', views.get_location_path),
    path('nearby-famous-locations', views.get_nearby_famous_locations)
]
