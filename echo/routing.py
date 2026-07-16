from channels.routing import ProtocolTypeRouter, URLRouter

from apps.chat.routing import websockets

application = ProtocolTypeRouter({
    "websocket": websockets,
})
