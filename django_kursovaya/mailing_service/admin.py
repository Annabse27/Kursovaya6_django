from django.contrib import admin
from .models import Client, Message, MailingSettings, MailingAttempt

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
   list_display = ('email', 'name', 'owner')
   list_filter = ('owner',)  # Фильтр по владельцу
   search_fields = ('email', 'name')  # Поиск по email и имени

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
   list_display = ('theme', 'owner')
   list_filter = ('owner',)  # Фильтр по владельцу
   search_fields = ('theme', 'owner__username')  # Поиск по теме и пользователю

@admin.register(MailingSettings)
class MailingSettingsAdmin(admin.ModelAdmin):
   list_display = ('start_datetime', 'end_datetime', 'periodicity', 'mailing_status', 'owner')
   list_filter = ('periodicity', 'mailing_status', 'owner')  # Фильтр по периодичности, статусу и владельцу
   search_fields = ('owner__username', 'message__theme')  # Поиск по владельцу и теме сообщения

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
   list_display = ('mailing', 'datetime_last_try', 'attempt_status')
   list_filter = ('attempt_status',)  # Фильтр по статусу попытки
   search_fields = ('mailing__message__theme',)  # Поиск по теме сообщения рассылки
