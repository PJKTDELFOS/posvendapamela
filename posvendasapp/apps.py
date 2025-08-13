from django.apps import AppConfig


class PosvendasappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posvendasapp'

    def ready(self):
        import posvendasapp.signals
        from utils.tools_utils import criar_grupos
        criar_grupos()
