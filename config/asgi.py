import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import main.routing  # noqa

application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": AuthMiddlewareStack(URLRouter(main.routing.websocket_urlpatterns))}
)
