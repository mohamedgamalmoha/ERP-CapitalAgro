from django.apps import AppConfig


class WorkstationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workstation'

    def ready(self):
        import workstation.signals
