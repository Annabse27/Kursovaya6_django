from django.contrib import admin
from .models import Client, Message, Mailing, Attempt

class ClientInline(admin.TabularInline):
    """
    Класс для добавления клиентов к рассылке через интерфейс администратора.
    Используется в модели Mailing для удобного добавления клиентов.
    """
    model = Mailing.clients.through
    extra = 1
    verbose_name = "Client"
    verbose_name_plural = "Clients"

class MailingAdmin(admin.ModelAdmin):
    """
    Класс для настройки отображения модели Mailing в админ панели.
    Отображает список рассылок с полями 'name', 'start_time', 'status', 'periodicity'.
    """
    list_display = ('name', 'start_time', 'status', 'periodicity')
    list_filter = ('status', 'periodicity')
    search_fields = ('name',)
    inlines = [ClientInline]

# Регистрация моделей в админке для их управления через панель администратора
admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Mailing, MailingAdmin)
admin.site.register(Attempt)
