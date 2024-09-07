from django.db import models

class Client(models.Model):
    """
    Это модель для хранения информации о клиентах, которые будут получать рассылки.
    """
    email = models.EmailField(unique=True, verbose_name="Email клиента")
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.full_name


class Message(models.Model):
    """
    Это модель для хранения сообщений, которые будут отправлены в рассылке.
    """
    subject = models.CharField(max_length=255, verbose_name="Тема сообщения")
    body = models.TextField(verbose_name="Тело сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """
    Это основная модель, представляющая рассылку.
    Она связывает клиентов и сообщения, а также содержит информацию о расписании.
    """
    PERIODICITY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        # Можно добавить другие опции
    ]


    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название рассылки")
    start_time = models.DateTimeField(verbose_name="Дата и время начала")
    periodicity = models.CharField(max_length=50, choices=PERIODICITY_CHOICES, verbose_name="Периодичность")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings", verbose_name="Сообщение")
    clients = models.ManyToManyField(Client, related_name="mailings", verbose_name="Клиенты")

    def __str__(self):
        return self.name


class Attempt(models.Model):
    """
    Эта модель будет хранить информацию о попытках отправки рассылок,
    включая статус и ответ сервера.

    """
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts", verbose_name="Рассылка")
    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    success = models.BooleanField(default=False, verbose_name="Успешно")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ сервера")

    def __str__(self):
        return f"Попытка {self.mailing.name} в {self.attempted_at}"


