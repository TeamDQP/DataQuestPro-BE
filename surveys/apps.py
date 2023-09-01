from django.apps import AppConfig


class SurveysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'surveys'

    def ready(self):
        from . import operator