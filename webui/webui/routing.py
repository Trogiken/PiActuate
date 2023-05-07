from django.urls import re_path

from controls import consumers

websocket_urlpatterns = [
    re_path(r"ws/engine/door/", consumers.DoorConsumer.as_asgi()),
]