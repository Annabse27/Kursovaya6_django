from django.db import models
from django.conf import settings

class Client(models.Model):
    """
    Модель для хранения информации о клиентах, которые подписаны на рассылку.
    Включает поля для email, полного имени, комментария и даты создания.
    """
    email = models.EmailField(unique=True, verbose_name="Email клиента")
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")  # Поле для блокировки клиента

    def __str__(self):
        """
        Возвращает полное имя клиента для удобного отображения в интерфейсе.
        """
        return self.full_name

class Message(models.Model):
    """
    Модель для хранения сообщений, которые отправляются в рамках рассылки.
    Включает тему, текст сообщения и дату создания.
    """
    subject = models.CharField(max_length=255, verbose_name="Тема сообщения")
    body = models.TextField(verbose_name="Тело сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        """
        Возвращает тему сообщения для удобного отображения.
        """
        return self.subject

class Mailing(models.Model):
    """
    Основная модель для рассылок, связывает сообщения и клиентов.
    Содержит информацию о названии, времени начала, статусе и периодичности рассылки.
    """
    PERIODICITY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
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
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец'
    )

    def __str__(self):
        """
        Возвращает название рассылки для удобного отображения.
        """
        return self.name

class Attempt(models.Model):
    """
    Модель для хранения информации о попытках отправки рассылок.
    Включает дату и время попытки, статус успеха и ответ сервера.
    """
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts", verbose_name="Рассылка")
    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    success = models.BooleanField(default=False, verbose_name="Успешно")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ сервера")

    def __str__(self):
        """
        Возвращает информацию о попытке для удобного отображения.
        """
        return f"Попытка {self.mailing.name} в {self.attempted_at}"
