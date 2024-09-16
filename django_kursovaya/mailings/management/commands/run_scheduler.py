import logging
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from mailings.tasks import check_scheduled_mailings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Запускает планировщик для проверки рассылок"

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_scheduled_mailings, 'interval', minutes=10)
        scheduler.start()

        logger.info("Планировщик запущен для проверки рассылок каждые 10 минут.")

        # Останавливаем планировщик при остановке сервера
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("Планировщик остановлен.")
