from django.apps import AppConfig


class EchoConfig(AppConfig):
    name = 'apps.core'
    verbose_name = 'core'

    def ready(self):
        print('initializing core app')
        import apps.core.signals  # noqa
