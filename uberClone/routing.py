from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import trip.routing
from trip.token_authentication import TokenAuthMiddleware

asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': asgi_app,
    'websocket': TokenAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                trip.routing.websocket_urlpatterns
            )
        ),
    )
})
