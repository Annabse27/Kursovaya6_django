'''import logging
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from mailing_service.tasks import change_mailing_status, send_mailing

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Запускает планировщик для проверки и отправки рассылок"

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()

        # Добавляем задачу для изменения статусов рассылок каждые 10 минут
        scheduler.add_job(change_mailing_status, 'interval', minutes=10, id='change_mailing_status')
        logger.info("Задача по обновлению статусов рассылок добавлена в планировщик.")

        # Добавляем задачу для отправки рассылок каждые 10 минут
        scheduler.add_job(send_mailing, 'interval', minutes=10, id='send_mailing')
        logger.info("Задача по отправке рассылок добавлена в планировщик.")

        scheduler.start()
        logger.info("Планировщик запущен для рассылок.")

        try:
            while True:
                pass  # Держим планировщик активным
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("Планировщик остановлен.")
'''