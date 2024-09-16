from django.core.mail import send_mail
from django.utils import timezone
import logging
from .models import Mailing

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_mailing(mailing_id):
    logger.info(f"Запуск задачи отправки писем для рассылки с ID: {mailing_id}")

    try:
        mailing = Mailing.objects.get(id=mailing_id)
        logger.debug(f"Получена рассылка: {mailing}")
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена.")
        return

    if mailing.status != 'created':
        logger.warning(f"Рассылка с ID {mailing_id} уже обработана или не находится в статусе 'created'. Текущий статус: {mailing.status}")
        return

    mailing.status = 'started'
    mailing.save()

    clients = mailing.clients.all()
    subject = mailing.message.subject
    body = mailing.message.body

    for client in clients:
        try:
            send_mail(
                subject,
                body,
                'your-email@example.com',
                [client.email],
                fail_silently=False,
            )
            logger.info(f"Письмо успешно отправлено клиенту: {client.email}")
        except Exception as e:
            logger.error(f"Ошибка при отправке письма клиенту {client.email}: {e}")

    mailing.status = 'completed'
    mailing.save()
    logger.info(f"Рассылка с ID {mailing_id} успешно завершена.")

def check_scheduled_mailings():
    logger.debug("Запуск проверки запланированных рассылок.")
    current_time = timezone.now()

    mailings = Mailing.objects.filter(status='created', start_time__lte=current_time)
    logger.debug(f"Найдено {mailings.count()} рассылок для отправки.")

    for mailing in mailings:
        logger.debug(f"Проверка рассылки с ID: {mailing.id}")
        send_mailing(mailing.id)
