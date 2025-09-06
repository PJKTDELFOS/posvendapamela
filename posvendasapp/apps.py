from django.apps import AppConfig


class PosvendasappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posvendasapp'

    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError
        from django.contrib.auth.models import Group
        from utils.tools_utils import criar_grupos

        try:
            criar_grupos()
        except (OperationalError, ProgrammingError):
            # Ignora se o banco ainda não estiver pronto
            pass

