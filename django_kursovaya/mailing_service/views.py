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
        # Обычные пользователи видят только свои сообщения, суперпользователи видят все
        return Message.objects.filter(owner=user) if not user.is_superuser else Message.objects.all()


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing_utils/message_detail.html'  # Путь к шаблону

    def get_object(self, queryset=None):
        message = super().get_object(queryset)
        # Проверяем, является ли пользователь владельцем сообщения или суперпользователем
        if message.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("У вас нет прав для просмотра этого сообщения.")
        return message


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
        # Обычные пользователи видят только свои рассылки
        return MailingSettings.objects.filter(owner=user)

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

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.start_datetime = form.cleaned_data['start_datetime']
        form.instance.end_datetime = form.cleaned_data['end_datetime']

        # Обычные пользователи могут создать рассылку только с начальным статусом "Создана"
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name='Manager').exists():
            form.instance.mailing_status = 'created'

        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # Фильтруем клиентов для обычных пользователей
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name='Manager').exists():
            form.fields['clients'].queryset = Client.objects.filter(owner=self.request.user)
        return form

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

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.start_datetime = form.cleaned_data['start_datetime']
        mailing.end_datetime = form.cleaned_data['end_datetime']

        # Обычные пользователи не могут изменять статус рассылки, только менеджеры и суперпользователи
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Manager').exists():
            mailing.mailing_status = form.cleaned_data['mailing_status']
        else:
            # Обычные пользователи могут сохранять только свои рассылки в статусе "created"
            if mailing.mailing_status != 'created':
                mailing.mailing_status = 'created'

        mailing.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # Обычным пользователям показываем только их клиентов
        if not self.request.user.is_superuser and not self.request.user.groups.filter(name='Manager').exists():
            form.fields['clients'].queryset = Client.objects.filter(owner=self.request.user)
        return form

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
