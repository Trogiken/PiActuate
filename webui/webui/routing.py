from django.urls import re_path

from controls import consumers

websocket_urlpatterns = [
    re_path(r"ws/api/door/", consumers.DoorConsumer.as_asgi()),
    re_path(r"ws/api/update/", consumers.UpdateConsumer.as_asgi())
]