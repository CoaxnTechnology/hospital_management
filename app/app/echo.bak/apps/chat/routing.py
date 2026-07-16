from django.urls import path, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import ChatConsumer, EventConsumer

websockets = URLRouter([
    re_path(r'ws/discussion/(?P<id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/events/(?P<id>\w+)/$', EventConsumer.as_asgi()),
])
