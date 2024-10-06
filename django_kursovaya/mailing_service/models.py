from django.db import models
from users.models import CustomUser  # Убедись, что имя модели соответствует проекту

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=150, verbose_name="Имя клиента")
    comments = models.TextField(verbose_name="Комментарии", **NULLABLE)
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, verbose_name="Владелец", **NULLABLE)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Message(models.Model):
    theme = models.CharField(max_length=255, verbose_name="Тема")
    body = models.TextField(verbose_name="Тело сообщения")
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, verbose_name="Владелец", **NULLABLE)

    def __str__(self):
        return self.theme

class MailingSettings(models.Model):
    PERIODS = (('daily', 'Ежедневно'), ('weekly', 'Еженедельно'), ('monthly', 'Ежемесячно'))
    STATUSES = (('created', 'Создана'), ('launched', 'Запущена'), ('completed', 'Завершена'))

    start_datetime = models.DateTimeField(verbose_name="Дата и время начала")
    end_datetime = models.DateTimeField(verbose_name="Дата и время окончания")
    periodicity = models.CharField(max_length=20, choices=PERIODS, default='daily', verbose_name="Периодичность")
    mailing_status = models.CharField(max_length=20, choices=STATUSES, default='created', verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    clients = models.ManyToManyField(Client, related_name='mailing_utils', verbose_name="Клиенты для рассылки")
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, verbose_name="Владелец", **NULLABLE)

    def __str__(self):
        return f"Рассылка {self.pk} ({self.get_periodicity_display()})"

class MailingAttempt(models.Model):
    STATUS_CHOICES = (('success', 'Успешно'), ('failure', 'Неудача'))

    mailing = models.ForeignKey(MailingSettings, on_delete=models.CASCADE, verbose_name="Рассылка")
    datetime_last_try = models.DateTimeField(auto_now=True, verbose_name="Дата последней попытки")
    attempt_status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Статус попытки")
    response_mail_server = models.TextField(verbose_name="Ответ почтового сервера", **NULLABLE)

    def __str__(self):
        return f"Попытка {self.pk} - {self.get_attempt_status_display()}"

