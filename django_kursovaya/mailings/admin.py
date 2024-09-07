from django.contrib import admin
from .models import Client, Message, Mailing, Attempt



class ClientInline(admin.TabularInline):
    model = Mailing.clients.through
    extra = 1
    verbose_name = "Client"
    verbose_name_plural = "Clients"


class MailingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'status', 'periodicity')
    list_filter = ('status', 'periodicity')
    search_fields = ('name',)
    inlines = [ClientInline]

admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Mailing, MailingAdmin)
admin.site.register(Attempt)
