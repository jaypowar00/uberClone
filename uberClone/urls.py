from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('user/', include('user.urls')),
    path('trip/', include('trip.urls')),
    path('driver/', include('driver.urls')),
    path('ride/', include('ride.urls')),
    path('admin/', admin.site.urls),
]
