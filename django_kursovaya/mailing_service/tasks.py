import logging
from .models import MailingSettings, MailingAttempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def change_mailing_status():
    logger.info("Функция change_mailing_status вызвана.")  # Новый отладочный вывод
    now = timezone.now()
    mailings = MailingSettings.objects.filter(mailing_status='created', start_datetime__lte=now)
    logger.info(f"Найдено рассылок для запуска: {mailings.count()}")
    for mailing in mailings:
        mailing.mailing_status = 'launched'
        mailing.save()
        logger.info(f"Рассылка {mailing.id} запущена.")

    # Обновляем статусы завершенных рассылок
    completed_mailings = MailingSettings.objects.filter(end_datetime__lte=now)
    for mailing in completed_mailings:
        mailing.mailing_status = 'completed'
        mailing.save()
        logger.info(f"Рассылка {mailing.id} завершена.")

def send_mailing():
    logger.info("Функция send_mailing вызвана.")  # Новый отладочный вывод
    mailings = MailingSettings.objects.filter(mailing_status='launched')
    logger.info(f"Найдено запущенных рассылок: {mailings.count()}")
    for mailing in mailings:
        recipients = [client.email for client in mailing.clients.all()]
        logger.info(f"Отправка для {recipients}")
        send_mail(
            subject=mailing.message.theme,
            message=mailing.message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        #Успешная отправка
        attempt = MailingAttempt.objects.create(
            mailing=mailing,
            attempt_status='success',
            datetime_last_try=timezone.now(),
            response_mail_server="Отправлено успешно"
        )
        logger.info(f"Рассылка {mailing.id} отправлена.")

