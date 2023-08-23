from django.apps import AppConfig


class BaseConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        import notification.signals
