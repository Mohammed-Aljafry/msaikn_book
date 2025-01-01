"""
توجيه WebSocket للمشروع
"""

from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from properties.consumers import PropertyConsumer
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/properties/$', PropertyConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})