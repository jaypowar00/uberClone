from django.urls import path
from . import views

urlpatterns = [
    path('user', views.get_user_ride),
    path('driver', views.get_driver_ride),
    path('book', views.book_ride),
    path('cancel', views.cancel_ride),
    path('generate-otp', views.generate_otp),
    path('verify-otp', views.verify_otp),
    path('user-history', views.user_ride_history),
    path('driver-history', views.driver_ride_history),
]
