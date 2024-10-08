import os
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from .models import MailingSettings, MailingAttempt


class Command(BaseCommand):
    help = 'Send scheduled mailings'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # Находим все запущенные рассылки
        active_mailings = MailingSettings.objects.filter(
            mailing_status='launched',
            start_datetime__lte=now,
            end_datetime__gte=now,
        )

        from_email = os.getenv('EMAIL_HOST_USER', 'default@example.com')

        for mailing in active_mailings:
            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject=mailing.message.theme,
                        message=mailing.message.body,
                        from_email=from_email,
                        recipient_list=[client.email],
                    )
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        attempt_status='success',
                        response_mail_server='Email sent successfully',
                    )
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        attempt_status='failure',
                        response_mail_server=str(e),
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent mailings. Processed {active_mailings.count()} mailings.'))
