from django.urls import path

from main import consumers

websocket_urlpatterns = [
    path("ws/", consumers.PoJsonConsumer.as_asgi()),
]
