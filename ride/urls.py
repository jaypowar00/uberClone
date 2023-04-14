from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_ride),
    path('book', views.book_ride),
    path('cancel', views.cancel_ride),
    path('generate-otp', views.generate_otp),
    path('verify-otp', views.verify_otp),
    path('history', views.get_ride_history),
    path('payment/pay', views.pay_ride)
]
