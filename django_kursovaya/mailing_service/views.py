from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


from .models import Client, Message, MailingSettings, MailingAttempt
from .forms import ClientForm, MessageForm, MailingSettingsForm
from django.views.generic import TemplateView
from blog.models import BlogPost
from django.shortcuts import redirect

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

import os  # Для работы с переменными окружения
from django.core.mail import send_mail  # Для отправки писем
from django.utils import timezone  # Для работы с датами и временем в Django


# Функции блокировки и разблокировки клиента
@login_required
def block_client_view(request, pk):
    """Блокировка клиента менеджером или администратором."""
    if not request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
        raise PermissionDenied("У вас нет прав для блокировки клиентов.")

    client = get_object_or_404(Client, pk=pk)
    client.is_active = False
    client.save()
    return redirect('mailing_service:clients')


@login_required
def unblock_client_view(request, pk):
    """Разблокировка клиента менеджером или администратором."""
    if not request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
        raise PermissionDenied("У вас нет прав для разблокировки клиентов.")

    client = get_object_or_404(Client, pk=pk)
    client.is_active = True
    client.save()
    return redirect('mailing_service:clients')



# --- Вьюхи для клиентов ---
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing_utils/client_list.html'

    def get_queryset(self):
        user = self.request.user
        # Суперпользователи и менеджеры видят всех клиентов
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return Client.objects.all()
        # Обычные пользователи видят только своих клиентов
        return Client.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        context['is_client'] = self.request.user.groups.filter(name='Client').exists()
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing_utils/client_detail.html'

    def get_object(self, queryset=None):
        user = self.request.user
        client = super().get_object(queryset)
        # Суперпользователи и менеджеры могут видеть всех клиентов
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return client
        # Обычные пользователи могут видеть только своих клиентов
        if client.owner == user:
            return client
        else:
            raise PermissionDenied("У вас нет прав для просмотра этого клиента.")


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing_utils/client_form.html'
    success_url = reverse_lazy('mailing_service:clients')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        # Если пользователь не суперпользователь и не менеджер, создаем неактивного клиента
        if not user.is_superuser and not user.groups.filter(name='Manager').exists():
            form.instance.is_active = False
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        context['is_client'] = self.request.user.groups.filter(name='Client').exists()
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing_utils/client_form.html'
    success_url = reverse_lazy('mailing_service:clients')

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        # Разрешаем редактировать только менеджерам и суперпользователям
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("У вас нет прав для редактирования клиентов.")

    def form_valid(self, form):
        # Получаем оригинального владельца клиента перед обновлением
        original_owner = form.instance.owner
        form.instance.owner = original_owner  # Сохраняем оригинального владельца
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        return context

    def get_object(self, queryset=None):
        user = self.request.user
        client = super().get_object(queryset)
        # Разрешаем редактировать только менеджерам и суперпользователям
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return client
        else:
            raise PermissionDenied("У вас нет прав для редактирования этого клиента.")


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'mailing.delete_client'
    template_name = 'mailing_utils/client_confirm_delete.html'
    success_url = reverse_lazy('mailing_service:clients')

    def get_object(self, queryset=None):
        user = self.request.user
        client = super().get_object(queryset)
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return client
        if client.owner == user:
            return client
        else:
            raise PermissionDenied("У вас нет прав для удаления этого клиента.")


# --- Вьюхи для сообщений ---

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing_utils/message_list.html'  # Путь к шаблону

    def get_queryset(self):
        user = self.request.user
        # Менеджеры и суперпользователи видят все сообщения, обычные пользователи — только свои
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Проверяем, является ли пользователь клиентом или администратором
        context['is_client'] = user.groups.filter(name='Client').exists() or user.is_superuser
        return context


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing_utils/message_detail.html'  # Путь к шаблону

    def get_object(self, queryset=None):
        message = super().get_object(queryset)
        # Проверяем, является ли пользователь владельцем сообщения, менеджером или суперпользователем
        if message.owner != self.request.user and not (
                self.request.user.is_superuser or self.request.user.groups.filter(name='Manager').exists()):
            raise PermissionDenied("У вас нет прав для просмотра этого сообщения.")
        return message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser_or_manager'] = self.request.user.is_superuser or self.request.user.groups.filter(name='Manager').exists()
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing_utils/message_form.html'  # Путь к шаблону
    success_url = reverse_lazy('mailing_service:messages')

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Устанавливаем владельца сообщения
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing_utils/message_form.html'  # Путь к шаблону
    success_url = reverse_lazy('mailing_service:messages')

    def dispatch(self, request, *args, **kwargs):
        message = self.get_object()
        # Проверка прав на редактирование сообщения
        if message.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для редактирования этого сообщения.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Устанавливаем владельца
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing_utils/message_confirm_delete.html'  # Путь к шаблону
    success_url = reverse_lazy('mailing_service:messages')

    def dispatch(self, request, *args, **kwargs):
        message = self.get_object()
        # Проверка прав на удаление сообщения
        if message.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для удаления этого сообщения.")
        return super().dispatch(request, *args, **kwargs)



# --- Вьюхи для настроек рассылок ---

class MailingSettingsListView(LoginRequiredMixin, ListView):
    model = MailingSettings
    template_name = 'mailing_utils/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        # Менеджеры и суперпользователи видят все рассылки
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return MailingSettings.objects.all()
        # Обычные пользователи видят только свои рассылки, независимо от статуса
        return MailingSettings.objects.filter(owner=user)  # Убираем проверку на статус

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о роли пользователя
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        context['is_client'] = self.request.user.groups.filter(name='Client').exists()
        return context


class MailingSettingsDetailView(LoginRequiredMixin, DetailView):
    model = MailingSettings
    template_name = 'mailing_utils/mailing_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['mailing'] = mailing

        # Проверка, может ли рассылка быть деактивирована
        context['can_deactivate'] = mailing.mailing_status == 'launched'

        # Добавляем информацию о правах пользователя
        context['is_superuser'] = self.request.user.is_superuser
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()

        return context

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()

        # Проверяем, имеет ли пользователь право изменять статус рассылки
        if request.user.is_superuser or request.user.groups.filter(name='Manager').exists():
            if 'deactivate' in request.POST and mailing.mailing_status == 'launched':
                mailing.mailing_status = 'deactivated'
                mailing.save()
            elif 'activate' in request.POST and mailing.mailing_status == 'deactivated':
                mailing.mailing_status = 'launched'
                mailing.save()

        return redirect('mailing_service:view_setting', pk=mailing.pk)


class MailingSettingsCreateView(LoginRequiredMixin, CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    template_name = 'mailing_utils/mailing_form.html'
    success_url = reverse_lazy('mailing_service:settings')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # Обычные пользователи видят только своих клиентов
        if not self.request.user.is_superuser:
            form.fields['clients'].queryset = Client.objects.filter(owner=self.request.user, is_active=True)
            form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        else:
            # Администраторы видят всех активных клиентов
            form.fields['clients'].queryset = Client.objects.filter(is_active=True)

        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.start_datetime = form.cleaned_data['start_datetime']
        form.instance.end_datetime = form.cleaned_data['end_datetime']

        # Приводим start_datetime и end_datetime к одному типу (offset-aware)
        if form.instance.start_datetime.tzinfo is None:
            form.instance.start_datetime = timezone.make_aware(form.instance.start_datetime)
        if form.instance.end_datetime.tzinfo is None:
            form.instance.end_datetime = timezone.make_aware(form.instance.end_datetime)

        # Обычные пользователи могут создать рассылку только со статусом "Создана"
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name='Manager').exists():
            form.instance.mailing_status = 'created'

        # Сначала сохраняем рассылку
        response = super().form_valid(form)

        # Проверяем дату и время после создания
        now = timezone.now()
        mailing = self.object

        if mailing.start_datetime <= now <= mailing.end_datetime:
            # Отправка писем клиентам, если текущее время между началом и окончанием рассылки
            from_email = os.getenv('EMAIL_HOST_USER', 'default@example.com')
            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject=mailing.message.theme,
                        message=mailing.message.body,
                        from_email=from_email,
                        recipient_list=[client.email],
                    )
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        attempt_status='success',
                        response_mail_server='Email sent successfully',
                    )
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        attempt_status='failure',
                        response_mail_server=str(e),
                    )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        context['is_client'] = self.request.user.groups.filter(name='Client').exists()
        return context


class MailingSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    template_name = 'mailing_utils/mailing_form.html'
    success_url = reverse_lazy('mailing_service:settings')


    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # Обычные пользователи видят только своих клиентов
        if not self.request.user.is_superuser:
            form.fields['clients'].queryset = Client.objects.filter(owner=self.request.user, is_active=True)
            form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        else:
            # Администраторы видят всех активных клиентов
            form.fields['clients'].queryset = Client.objects.filter(is_active=True)
        return form

    def form_valid(self, form):
        mailing = form.save(commit=False)
        print(f'Перед изменением: Статус: {mailing.mailing_status}, Владелец: {mailing.owner}')  # Отладочный вывод

        #mailing.owner = self.request.user
        # Не изменяем владельца, если он уже установлен
        if not mailing.owner:
            mailing.owner = self.request.user

        mailing.start_datetime = form.cleaned_data['start_datetime']
        mailing.end_datetime = form.cleaned_data['end_datetime']

        # Приводим start_datetime и end_datetime к одному типу (offset-aware)
        if mailing.start_datetime.tzinfo is None:
            mailing.start_datetime = timezone.make_aware(mailing.start_datetime)
        if mailing.end_datetime.tzinfo is None:
            mailing.end_datetime = timezone.make_aware(mailing.end_datetime)

        # Обычные пользователи не могут изменять статус рассылки, только менеджеры и суперпользователи
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Manager').exists():
            mailing.mailing_status = form.cleaned_data['mailing_status']
        else:
            if mailing.mailing_status != 'created':
                mailing.mailing_status = 'created'

        mailing.save()
        form.save_m2m()
        print(f'После изменения: Статус: {mailing.mailing_status}, Владелец: {mailing.owner}')  # Отладочный вывод
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        context['is_client'] = self.request.user.groups.filter(name='Client').exists()
        return context


class MailingSettingsDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingSettings
    template_name = 'mailing_utils/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_service:settings')

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)
        # Проверяем, является ли пользователь владельцем рассылки
        if self.request.user == mailing.owner or self.request.user.is_superuser:
            return mailing
        else:
            raise PermissionDenied("У вас нет прав для удаления этой рассылки.")


# --- Вьюха для попыток ---
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailing_utils/mailingattempt_list.html'

    def get_queryset(self):
        mailing_id = self.kwargs.get('pk')  # Получаем ID рассылки из URL
        user = self.request.user
        # Менеджеры и суперпользователи могут видеть все попытки отправки
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            queryset = MailingAttempt.objects.filter(mailing__id=mailing_id)
        else:
            queryset = MailingAttempt.objects.filter(mailing__id=mailing_id, mailing__owner=user)
        return queryset



# --- Вьюха для отчета ---
class ReportView(TemplateView):
   template_name = 'mailing_utils/report_list.html'  # Подключаем твой шаблон


   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['mailing_count'] = MailingSettings.objects.count()
       context['active_mailing_count'] = MailingSettings.objects.filter(mailing_status='launched').count()
       context['unique_clients_count'] = Client.objects.values('email').distinct().count()
       context['blog_list'] = BlogPost.objects.filter(is_published=True).order_by('?')[:3]
       return context
