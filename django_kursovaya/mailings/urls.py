from django.urls import path
from .views import (
    ClientListCreateView, ClientDetailView,
    MessageListCreateView, MessageDetailView,
    MailingListCreateView, MailingDetailView,
    AttemptListCreateView, AttemptDetailView
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
]
