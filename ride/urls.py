from django.urls import path
from . import views

urlpatterns = [
    path('book', views.book_ride),
    path('cancel', views.cancel_ride),
    path('generate-otp', views.generate_otp),
    path('verify-otp', views.verify_otp),
]
