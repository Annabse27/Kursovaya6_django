from django.core.mail import send_mail
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
import logging


# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_mailing(mailing_id):
    logger.info(f"Запуск задачи отправки писем для рассылки с ID: {mailing_id}")

    try:
        # Получаем рассылку
        mailing = Mailing.objects.get(id=mailing_id)
        logger.debug(f"Получена рассылка: {mailing}")

    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена.")
        return

    if mailing.status != 'created':
        logger.warning(f"Рассылка с ID {mailing_id} уже обработана или не находится в статусе 'created'. Текущий статус: {mailing.status}")
        return

    # Обновляем статус на 'started'
    mailing.status = 'started'
    mailing.save()

    # Получаем всех клиентов для отправки рассылки
    clients = mailing.clients.all()
    subject = mailing.message.subject
    body = mailing.message.body

    for client in clients:
        try:
            # Отправляем письмо каждому клиенту
            send_mail(
                subject,
                body,
                'your-email@example.com',  # Отправитель
                [client.email],  # Получатель
                fail_silently=False,
            )
            logger.info(f"Письмо успешно отправлено клиенту: {client.email}")
        except Exception as e:
            logger.error(f"Ошибка при отправке письма клиенту {client.email}: {e}")

    # Обновляем статус рассылки на 'completed' после завершения
    mailing.status = 'completed'
    mailing.save()
    logger.info(f"Рассылка с ID {mailing_id} успешно завершена.")



from .models import Mailing, Client

def check_scheduled_mailings():
    logger.debug("Запуск проверки запланированных рассылок.")
    current_time = timezone.now()

    # Фильтруем рассылки, которые находятся в статусе 'created' и их время наступило
    mailings = Mailing.objects.filter(status='created', start_time__lte=current_time)
    logger.debug(f"Найдено {mailings.count()} рассылок для отправки.")

    for mailing in mailings:
        logger.debug(f"Проверка рассылки с ID: {mailing.id}")
        send_mailing(mailing.id)

# Планировщик для регулярной проверки рассылок
scheduler = BackgroundScheduler()
scheduler.add_job(check_scheduled_mailings, 'interval', minutes=10)
scheduler.start()

logger.info("Планировщик запущен для регулярной проверки рассылок.")


def get_next_run_time(mailing):
    if mailing.periodicity == 'daily':
        scheduler.add_job(send_mailing, 'interval', days=1, args=[mailing])
    elif mailing.periodicity == 'weekly':
        scheduler.add_job(send_mailing, 'interval', weeks=1, args=[mailing])
