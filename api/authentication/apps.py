from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = "authentication"

    def ready(self):
        from . import receivers
