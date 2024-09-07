"""
Cоздадим представления для обработки CRUD операций.
Используем generics, чтобы упростить разработку.
"""

from rest_framework import generics
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Client, Message, Mailing, Attempt
from .serializers import ClientSerializer, MessageSerializer, MailingSerializer, AttemptSerializer
from .forms import MailingForm
from .tasks import check_scheduled_mailings, send_mailing


# Клиенты
class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


# Сообщения
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# Рассылки
class MailingListCreateView(generics.ListCreateAPIView):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer

class MailingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer


# Попытки отправки
class AttemptListCreateView(generics.ListCreateAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer

class AttemptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer



def create_mailing(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save()

            # Планируем рассылку или отправляем сразу, если время уже прошло
            if mailing.start_time > timezone.now():
                check_scheduled_mailings(mailing.id, mailing.start_time)
            else:
                send_mailing(mailing.id)
            return redirect('mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailing_form.html', {'form': form})
