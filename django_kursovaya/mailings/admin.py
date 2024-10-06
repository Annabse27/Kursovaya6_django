from django.contrib import admin
from .models import Client, Message, MailingSettings, MailingAttempt

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'owner')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('theme', 'owner')

@admin.register(MailingSettings)
class MailingSettingsAdmin(admin.ModelAdmin):
    list_display = ('start_datetime', 'end_datetime', 'periodicity', 'mailing_status', 'owner')

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'datetime_last_try', 'attempt_status')
