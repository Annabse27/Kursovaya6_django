from django.apps import AppConfig
from django.utils.autoreload import autoreload_started


class MailingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailings'

    def ready(self):
        from .tasks import check_scheduled_mailings

        # Обработчик сигнала должен принимать **kwargs
        def start_scheduler(**kwargs):
            check_scheduled_mailings()

        autoreload_started.connect(start_scheduler)
