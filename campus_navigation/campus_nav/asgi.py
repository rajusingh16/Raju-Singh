import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_nav.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

import tracker.routing


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(tracker.routing.websocket_urlpatterns)),
    }
)
