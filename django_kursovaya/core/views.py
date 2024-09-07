from django.conf import settings
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.http import HttpResponseForbidden
from mailings.models import Mailing, Attempt
from mailings.forms import MailingForm
import logging
from blog.models import BlogPost



# Представления для домашней страницы
def home(request):
    print("BASE_DIR:", settings.BASE_DIR)
    print("Template DIRS:", settings.TEMPLATES[0]['DIRS'])
    print("Looking for template at:", os.path.join(settings.BASE_DIR, 'templates', 'home.html'))
    return render(request, 'home.html')

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
    return render(request, 'mailing_list.html', {'mailings': mailings})

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

@login_required
def client_dashboard(request):
    return render(request, 'client_dashboard.html')


#Логика для случайного выбора статей на главной странице
def home(request):
    random_posts = BlogPost.objects.order_by('?')[:3]
    return render(request, 'home.html', {'random_posts': random_posts})
