from django.conf import settings


class ChatMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        request.ws_server_path = '{}://{}:{}/'.format(
            settings.CHAT_WS_SERVER_PROTOCOL,
            settings.CHAT_WS_SERVER_HOST,
            settings.CHAT_WS_SERVER_PORT,
        )

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)

        return response
