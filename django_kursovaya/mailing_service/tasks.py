import os
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import MailingSettings, MailingAttempt


@shared_task
def send_scheduled_mailings():
    """Задача для отправки запланированных рассылок"""
    now = timezone.now()

    # Находим все запущенные рассылки, которые еще не завершены
    active_mailings = MailingSettings.objects.filter(
        mailing_status='launched',
        start_datetime__lte=now,
        end_datetime__gte=now,
    )

    from_email = os.getenv('EMAIL_HOST_USER', 'default@example.com')

    for mailing in active_mailings:
        for client in mailing.clients.all():
            # Пытаемся отправить письмо
            try:
                send_mail(
                    subject=mailing.message.theme,
                    message=mailing.message.body,
                    from_email=from_email,
                    recipient_list=[client.email],
                )
                # Успешная попытка
                MailingAttempt.objects.create(
                    mailing=mailing,
                    attempt_status='success',
                    response_mail_server='Email sent successfully',
                )
            except Exception as e:
                # Ошибка при отправке
                MailingAttempt.objects.create(
                    mailing=mailing,
                    attempt_status='failure',
                    response_mail_server=str(e),
                )

    return f"Processed {active_mailings.count()} mailings."
