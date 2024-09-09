from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from mailings.models import Mailing, Attempt, Client
from mailings.forms import MailingForm
from blog.models import BlogPost
import logging
from django.core.cache import cache
from django.contrib.auth import logout

logger = logging.getLogger(__name__)

# Главная страница
@login_required
def home(request):
    """
    Отображает главную страницу с данными о рассылках, клиентах и случайными статьями из блога.
    Данные кэшируются для повышения производительности.
    """
    # Проверяем, состоит ли пользователь в группах
    is_admin = request.user.groups.filter(name='Admin').exists()
    is_manager = request.user.groups.filter(name='Manager').exists()
    is_client = request.user.groups.filter(name='Client').exists()

    # Проверка кэша для общего количества рассылок
    total_mailings = cache.get('total_mailings')
    if not total_mailings:
        total_mailings = Mailing.objects.count()
        cache.set('total_mailings', total_mailings, timeout=60 * 15)

    # Получение количества активных рассылок и уникальных клиентов
    active_mailings = Mailing.objects.filter(status='started').count()
    unique_clients = Client.objects.distinct().count()

    # Кэширование случайных статей блога
    random_posts = cache.get('random_posts')
    if not random_posts:
        random_posts = BlogPost.objects.order_by('?')[:3]
        cache.set('random_posts', random_posts, timeout=60 * 15)

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
        'random_posts': random_posts,
        'is_admin': is_admin,
        'is_manager': is_manager,
        'is_client': is_client,
    }
    return render(request, 'home.html', context)

# Профиль пользователя
@login_required
def profile(request):
    """
    Отображает страницу профиля пользователя.
    """
    return render(request, 'profile.html')

# Проверка, является ли пользователь администратором
def is_admin(user):
    """
    Возвращает True, если пользователь является администратором.
    """
    return user.is_staff

# Админ панель
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Отображает админ панель с общими статистическими данными.
    """
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status='started').count()
    unique_clients = Client.objects.distinct().count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
        'on_admin_dashboard': True,
        'is_admin': request.user.is_staff,
    }
    return render(request, 'admin_dashboard.html', context)

# Создание новой рассылки
@permission_required('mailings.add_mailing', raise_exception=True)
def create_mailing(request):
    """
    Позволяет администратору или менеджеру создать новую рассылку.
    """
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mailing-list')
    else:
        form = MailingForm()
    return render(request, 'mailing_form.html', {'form': form})

# Список всех рассылок
@login_required
def mailing_list(request):
    """
    Отображает список всех рассылок.
    """
    mailings = Mailing.objects.all()
    return render(request, 'mailings/mailing_list.html', {'mailings': mailings})

# Редактирование рассылки
@login_required
def edit_mailing(request, mailing_id):
    """
    Позволяет редактировать существующую рассылку.
    Доступно только владельцу рассылки.
    """
    mailing = get_object_or_404(Mailing, id=mailing_id)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect('mailing-list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing_form.html', {'form': form})

# Удаление рассылки
@login_required
def delete_mailing(request, mailing_id):
    """
    Позволяет удалить рассылку.
    """
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.delete()
    return redirect('mailing-list')

# Просмотр отчетов по рассылкам
@login_required
def report_list(request):
    """
    Отображает отчеты по попыткам рассылок.
    """
    attempts = Attempt.objects.all()
    return render(request, 'report_list.html', {'attempts': attempts})

# Проверка, является ли пользователь менеджером
def is_manager(user):
    """
    Возвращает True, если пользователь состоит в группе менеджеров.
    """
    return user.groups.filter(name='Manager').exists()

# Панель менеджера
@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    """
    Отображает панель менеджера с рассылками и списком клиентов.
    """
    mailings = Mailing.objects.all()
    clients = Client.objects.all()

    context = {
        'mailings': mailings,
        'clients': clients,
        'on_manager_dashboard': True,
    }
    return render(request, 'manager_dashboard.html', context)

# Отключение рассылки
@login_required
@user_passes_test(is_manager)
def disable_mailing(request, mailing_id):
    """
    Отключает рассылку. Доступно менеджерам.
    """
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.status = 'disabled'
    mailing.save()
    return redirect('manager_dashboard')

# Блокировка пользователя
@login_required
@user_passes_test(is_manager)
def block_user(request, client_id):
    """
    Блокирует пользователя (клиента). Доступно менеджерам.
    """
    client = get_object_or_404(Client, id=client_id)
    if client.is_active:
        client.is_active = False
        client.save()
    return redirect('manager_dashboard')

# Проверка, является ли пользователь клиентом
def is_client(user):
    """
    Возвращает True, если пользователь состоит в группе клиентов.
    """
    return user.groups.filter(name='Client').exists()

# Панель клиента
@login_required
@user_passes_test(is_client)
def client_dashboard(request):
    """
    Отображает панель клиента с его рассылками.
    """
    mailings = request.user.mailings.all()

    context = {
        'mailings': mailings,
        'on_client_dashboard': True,
    }
    return render(request, 'client_dashboard.html', context)

# Список активных рассылок
@login_required
def active_mailings(request):
    """
    Отображает список активных рассылок.
    """
    mailings = Mailing.objects.filter(status='started')
    return render(request, 'mailings/active_mailings.html', {'mailings': mailings})

# Список клиентов
@login_required
def client_list(request):
    """
    Отображает список всех клиентов.
    """
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

# Список пользователей для админа
@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    """
    Отображает список пользователей для админа.
    """
    users = User.objects.all()
    return render(request, 'admin_user_list.html', {'users': users})

# Публикации клиента
@login_required
@user_passes_test(is_client)
def client_publications(request):
    """
    Отображает публикации, связанные с клиентом.
    """
    publications = BlogPost.objects.filter(author=request.user)
    return render(request, 'client_publications.html', {'publications': publications})

# Кастомный выход из системы
def custom_logout(request):
    """
    Выполняет выход пользователя из системы и перенаправляет на главную страницу.
    """
    logout(request)
    return redirect('home')
