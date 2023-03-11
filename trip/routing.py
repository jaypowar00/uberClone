from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live-location/(?P<ride_id>\w+)/$', consumers.LiveLocationConsumer.as_asgi()),
    re_path(r'ws/idle-driver/$', consumers.IdleDriverConsumer.as_asgi()),
]
