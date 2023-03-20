from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('user/', include('user.urls')),
    path('trip/', include('trip.urls')),
    path('driver/', include('driver.urls')),
    path('ride/', include('ride.urls')),
    path('admin/', admin.site.urls),
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path('schema/docs/', SpectacularSwaggerView.as_view(url_name="schema")),
]
