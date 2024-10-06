from django.shortcuts import render

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Client, Message, MailingSettings, MailingAttempt
from .forms import ClientForm, MessageForm, MailingSettingsForm
from django.views.generic import TemplateView
from blog.models import BlogPost

def home(request):
    return render(request, 'home.html')


# --- Вьюхи для клиентов ---
class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Client
    permission_required = 'mailing.view_client'
    template_name = 'mailings/client_list.html'

    def get_queryset(self):
        user = self.request.user
        return Client.objects.filter(owner=user) if not user.is_superuser else Client.objects.all()


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Client
    permission_required = 'mailing.view_client'
    template_name = 'mailings/client_detail.html'


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    permission_required = 'mailing.add_client'
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:clients')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    permission_required = 'mailing.change_client'
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:clients')


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'mailing.delete_client'
    template_name = 'mailings/client_confirm_delete.html'
    success_url = reverse_lazy('mailings:clients')


# --- Вьюхи для сообщений ---
class MessageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Message
    permission_required = 'mailing.view_message'
    template_name = 'mailings/message_list.html'

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(owner=user) if not user.is_superuser else Message.objects.all()


class MessageDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Message
    permission_required = 'mailing.view_message'
    template_name = 'mailings/message_detail.html'


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    permission_required = 'mailing.add_message'
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:messages')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    permission_required = 'mailing.change_message'
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:messages')


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    permission_required = 'mailing.delete_message'
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:messages')


# --- Вьюхи для настроек рассылок ---
class MailingSettingsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MailingSettings
    permission_required = 'mailing.view_mailingsettings'
    template_name = 'mailings/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return MailingSettings.objects.all()
        else:
            return MailingSettings.objects.filter(owner=user)  # Фильтрация по владельцу


class MailingSettingsDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = MailingSettings
    permission_required = 'mailing.view_mailingsettings'
    template_name = 'mailings/mailing_detail.html'


class MailingSettingsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    permission_required = 'mailing.add_mailingsettings'
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:settings')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingSettingsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    permission_required = 'mailing.change_mailingsettings'
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:settings')


class MailingSettingsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = MailingSettings
    permission_required = 'mailing.delete_mailingsettings'
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:settings')


# --- Вьюха для попыток рассылок ---
class MailingAttemptListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MailingAttempt
    permission_required = 'mailing.view_mailingattempt'
    template_name = 'mailings/mailingattempt_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = MailingAttempt.objects.all()
        else:
            queryset = MailingAttempt.objects.filter(mailing__owner=user)

        print(queryset)  # Вывод в консоль для отладки
        return queryset


# --- Вьюха для отчета ---
class ReportView(TemplateView):
    template_name = 'mailings/report_list.html'  # Подключаем твой шаблон

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_count'] = MailingSettings.objects.count()
        context['active_mailing_count'] = MailingSettings.objects.filter(mailing_status='launched').count()
        context['unique_clients_count'] = Client.objects.values('email').distinct().count()
        context['blog_list'] = BlogPost.objects.filter(is_published=True).order_by('?')[:3]
        return context
