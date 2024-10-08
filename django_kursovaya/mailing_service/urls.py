from django.urls import path
from .views import (MessageListView, MessageCreateView, MessageDetailView, MessageUpdateView, MessageDeleteView,
                    ClientListView, ClientCreateView, ClientDetailView, ClientUpdateView, ClientDeleteView,
                    MailingSettingsListView, MailingSettingsCreateView, MailingSettingsDetailView,
                    MailingSettingsUpdateView, MailingSettingsDeleteView, MailingAttemptListView, ReportView)


app_name = 'mailing_service'


urlpatterns = [
    path('clients/', ClientListView.as_view(), name='clients'),
    path('client/create/', ClientCreateView.as_view(), name='create_client'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='view_client'),
    path('client/<int:pk>/update/', ClientUpdateView.as_view(), name='update_client'),
    path('client/<int:pk>/delete/', ClientDeleteView.as_view(), name='delete_client'),


    path('messages/', MessageListView.as_view(), name='messages'),
    path('message/create/', MessageCreateView.as_view(), name='create_message'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='view_message'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='update_message'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='delete_message'),


    # Уникальные пути для рассылок
    path('settings/', MailingSettingsListView.as_view(), name='settings'),
    path('setting/create/', MailingSettingsCreateView.as_view(), name='create_setting'),
    path('setting/<int:pk>/', MailingSettingsDetailView.as_view(), name='view_setting'),
    path('setting/<int:pk>/update/', MailingSettingsUpdateView.as_view(), name='update_setting'),
    path('setting/<int:pk>/delete/', MailingSettingsDeleteView.as_view(), name='delete_setting'),

    #path('attempts/', MailingAttemptListView.as_view(), name='attempts'),
    path('setting/<int:pk>/attempts/', MailingAttemptListView.as_view(), name='attempts'),

    path('reports/', ReportView.as_view(), name='report'),  # Маршрут для отчёта
]
