from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from mailings.models import Mailing, Attempt, Client
from mailings.forms import MailingForm
from blog.models import BlogPost
import logging
from django.core.cache import cache


logger = logging.getLogger(__name__)


# Представления для домашней страницы
def home(request):
    # Проверяем, состоит ли пользователь в группах
    is_admin = request.user.groups.filter(name='Admin').exists()
    is_manager = request.user.groups.filter(name='Manager').exists()
    is_client = request.user.groups.filter(name='Client').exists()

    # Проверка кэша для общего количества рассылок
    total_mailings = cache.get('total_mailings')
    if not total_mailings:
        total_mailings = Mailing.objects.count()
        cache.set('total_mailings', total_mailings, timeout=60 * 15)

    # Остальная логика
    active_mailings = Mailing.objects.filter(status='started').count()
    unique_clients = Client.objects.distinct().count()

    # Кэширование статей блога
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



# Защита профиля пользователя с помощью @login_required
@login_required
def profile(request):
    return render(request, 'profile.html')

# Ограничение доступа только для администраторов с помощью @user_passes_test
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# Ограничение доступа на основе разрешений с помощью @permission_required
@permission_required('mailings.add_mailing', raise_exception=True)
def create_mailing(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mailing-list')
    else:
        form = MailingForm()
    return render(request, 'mailing_form.html', {'form': form})


# Защита доступа к списку рассылок
@login_required
def mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, 'mailings/mailing_list.html', {'mailings': mailings})


# Ограничение доступа к редактированию рассылки (только для владельца)
@login_required
def edit_mailing(request, mailing_id):
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
    mailing = get_object_or_404(Mailing, id=mailing_id)
    mailing.delete()
    return redirect('mailing-list')


# Просмотр отчетов по рассылкам
@login_required
def report_list(request):
    attempts = Attempt.objects.all()
    return render(request, 'report_list.html', {'attempts': attempts})


# Проверка, является ли пользователь менеджером
def is_manager(user):
    return user.groups.filter(name='Manager').exists()

@user_passes_test(is_manager)
def manager_dashboard(request):
    #logging.debug(f"User {user.username} is checking if they are a manager.")
    return render(request, 'manager_dashboard.html')

def is_client(user):
    return user.groups.filter(name='Client').exists()

@login_required
def client_dashboard(request):
    return render(request, 'client_dashboard.html')


@login_required
def active_mailings(request):
    mailings = Mailing.objects.filter(status='started')
    return render(request, 'mailings/active_mailings.html', {'mailings': mailings})

# Вьюха для отображения списка клиентов
@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})
