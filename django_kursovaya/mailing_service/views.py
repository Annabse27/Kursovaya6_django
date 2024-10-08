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

    def dispatch(self, request, *args, **kwargs):
        # Проверка прав менеджера или суперпользователя
        user = request.user
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("У вас нет прав для просмотра клиентов.")

    def get_queryset(self):
        user = self.request.user
        # Разрешаем всем суперпользователям и менеджерам видеть всех клиентов
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return Client.objects.all()
        # Обычные пользователи могут видеть только своих клиентов
        return Client.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о том, является ли пользователь менеджером
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing_utils/client_detail.html'

    def get_object(self, queryset=None):
        user = self.request.user
        client = super().get_object(queryset)
        # Если пользователь является суперпользователем или менеджером, он может видеть всех клиентов
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return client
        # Обычные пользователи могут видеть только своих клиентов
        if client.owner == user:
            return client
        else:
            raise PermissionDenied("У вас нет прав для просмотра этого клиента.")


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    permission_required = 'mailing.add_client'
    template_name = 'mailing_utils/client_form.html'
    success_url = reverse_lazy('mailing_service:clients')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Проверяем, если пользователь суперпользователь или менеджер
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("У вас нет прав для создания клиентов.")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing_utils/client_form.html'
    success_url = reverse_lazy('mailing_service:clients')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем флаг для отображения менеджера
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        return context

    def get_object(self, queryset=None):
        user = self.request.user
        client = super().get_object(queryset)
        # Если пользователь является суперпользователем или менеджером, они могут редактировать всех клиентов
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return client
        # Обычные пользователи могут редактировать только своих клиентов
        if client.owner == user:
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
class MessageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
   model = Message
   permission_required = 'mailing.view_message'
   template_name = 'mailing_utils/message_list.html'  # Убедитесь, что путь к шаблону верный


   def get_queryset(self):
       user = self.request.user
       return Message.objects.filter(owner=user) if not user.is_superuser else Message.objects.all()


class MessageDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Message
    permission_required = 'mailing.view_message'
    template_name = 'mailing_utils/message_detail.html'  # Обновлено


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    permission_required = 'mailing.add_message'
    template_name = 'mailing_utils/message_form.html'  # Обновлено
    success_url = reverse_lazy('mailing_service:messages')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    permission_required = 'mailing.change_message'
    template_name = 'mailing_utils/message_form.html'  # Обновлено
    success_url = reverse_lazy('mailing_service:messages')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    permission_required = 'mailing.delete_message'
    template_name = 'mailing_utils/message_confirm_delete.html'  # Обновлено
    success_url = reverse_lazy('mailing_service:messages')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# --- Вьюхи для настроек рассылок ---
class MailingSettingsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
   model = MailingSettings
   permission_required = 'mailing.view_mailingsettings'
   template_name = 'mailing_utils/mailing_list.html'

   def has_permission(self):
       """Переопределяем метод, чтобы учесть права менеджера."""
       if self.request.user.groups.filter(name='Manager').exists():
           return True  # Разрешаем доступ менеджерам
       return super().has_permission()

   def get_queryset(self):
       user = self.request.user
       if user.is_superuser:
           return MailingSettings.objects.all()
       elif user.groups.filter(name='Manager').exists():
           return MailingSettings.objects.filter(owner=user)
       else:
           return MailingSettings.objects.none()


class MailingSettingsDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = MailingSettings
    permission_required = 'mailing.view_mailingsettings'
    template_name = 'mailing_utils/mailing_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()  # Получаем объект рассылки
        context['mailing'] = mailing

        # Проверяем статус рассылки и добавляем соответствующую логику в контекст
        if mailing.mailing_status == 'launched':
            context['can_deactivate'] = True  # Позволяем отображать кнопку деактивации
        else:
            context['can_deactivate'] = False  # Не отображаем кнопку деактивации для завершенных рассылок

        return context

    def post(self, request, *args, **kwargs):
        """Логика для управления статусом рассылки"""
        mailing = self.get_object()

        if 'deactivate' in request.POST and mailing.mailing_status == 'launched':
            # Деактивируем рассылку
            mailing.mailing_status = 'deactivated'
            mailing.save()
        elif 'activate' in request.POST and mailing.mailing_status == 'deactivated':
            # Активируем рассылку
            mailing.mailing_status = 'launched'
            mailing.save()

        return redirect('mailing_service:view_setting', pk=mailing.pk)


class MailingSettingsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    permission_required = 'mailing.add_mailingsettings'
    template_name = 'mailing_utils/mailing_form.html'
    success_url = reverse_lazy('mailing_service:settings')


    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.start_datetime = form.cleaned_data['start_datetime']
        form.instance.end_datetime = form.cleaned_data['end_datetime']
        return super().form_valid(form)


class MailingSettingsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
   model = MailingSettings
   form_class = MailingSettingsForm
   permission_required = 'mailing.change_mailingsettings'
   template_name = 'mailing_utils/mailing_form.html'
   success_url = reverse_lazy('mailing_service:settings')

   def form_valid(self, form):
       # Собираем данные о владельце и датах для сохранения
       mailing = form.save(commit=False)
       mailing.owner = self.request.user
       mailing.start_datetime = form.cleaned_data['start_datetime']
       mailing.end_datetime = form.cleaned_data['end_datetime']

       # Сохраняем объект рассылки
       mailing.save()

       # Сохраняем ManyToMany данные (например, клиентов)
       form.save_m2m()

       return super().form_valid(form)


class MailingSettingsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
   model = MailingSettings
   permission_required = 'mailing.delete_mailingsettings'
   template_name = 'mailing_utils/mailing_confirm_delete.html'
   success_url = reverse_lazy('mailing_service:settings')



# --- Вьюха для попыток ---
class MailingAttemptListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MailingAttempt
    permission_required = 'mailing.view_mailingattempt'
    template_name = 'mailing_utils/mailingattempt_list.html'

    def get_queryset(self):
        mailing_id = self.kwargs.get('pk')  # Получаем ID рассылки из URL
        user = self.request.user
        if user.is_superuser:
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
