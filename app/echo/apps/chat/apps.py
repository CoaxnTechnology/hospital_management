from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = 'apps.chat'
    verbose_name = 'chat'

    def ready(self):
        print('initializing chat app')
