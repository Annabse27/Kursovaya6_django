from django.apps import AppConfig
from django.utils.autoreload import autoreload_started

class MailingsConfig(AppConfig):
    """
    Конфигурация приложения Mailings.
    Используется для регистрации приложения и запуска задач.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailings'

    def ready(self):
        """
        Метод, вызываемый при готовности приложения.
        Настраивает автоматическую проверку запланированных рассылок.
        """
        from .tasks import check_scheduled_mailings

        def start_scheduler(**kwargs):
            """
            Запускает планировщик для проверки рассылок при каждом изменении кода во время разработки.
            """
            check_scheduled_mailings()

        autoreload_started.connect(start_scheduler)
