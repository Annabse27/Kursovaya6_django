from django.urls import path
from .views import (
    ClientListCreateView, ClientDetailView,
    MessageListCreateView, MessageDetailView,
    MailingListCreateView, MailingDetailView,
    AttemptListCreateView, AttemptDetailView
)
from core.views import (
    mailing_list, create_mailing, edit_mailing,
    delete_mailing, report_list
)

urlpatterns = [
    # Клиенты
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),

    # Сообщения
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),

    # Рассылки
    path('mailings/', MailingListCreateView.as_view(), name='mailing-list-create'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing-detail'),

    # Попытки отправки
    path('attempts/', AttemptListCreateView.as_view(), name='attempt-list-create'),
    path('attempts/<int:pk>/', AttemptDetailView.as_view(), name='attempt-detail'),

    # Для работы с рассылками и отчетами
    path('list/', mailing_list, name='mailing-list'),
    path('create/', create_mailing, name='mailing-create'),
    path('<int:mailing_id>/edit/', edit_mailing, name='mailing-edit'),
    path('<int:mailing_id>/delete/', delete_mailing, name='mailing-delete'),
    path('reports/', report_list, name='report-list'),
]
