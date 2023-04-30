from django.urls import re_path

from controls import consumers

websocket_urlpatterns = [
    re_path(r"ws/dashboard/status/", consumers.DashboardConsumer.as_asgi()),  # DEBUG
]