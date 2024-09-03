from django.conf import settings
import os
from django.shortcuts import render, get_object_or_404, redirect  # Добавлен import redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.http import HttpResponseForbidden
from mailings.models import Mailing, Attempt
from mailings.forms import MailingForm

# Представления для домашней страницы
def home(request):
    print("BASE_DIR:", settings.BASE_DIR)
    print("Template DIRS:", settings.TEMPLATES[0]['DIRS'])
    print("Looking for template at:", os.path.join(settings.BASE_DIR, 'templates', 'home.html'))

    return render(request, 'home.html')


# 1. Защита профиля пользователя с помощью @login_required
@login_required
def profile(request):
    return render(request, 'profile.html')


# 2. Ограничение доступа только для администраторов с помощью @user_passes_test
def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


# 3. Ограничение доступа на основе разрешений с помощью @permission_required
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

# 4. Защита доступа к списку рассылок
@login_required
def mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, 'mailing_list.html', {'mailings': mailings})

# 5. Ограничение доступа к редактированию рассылки (только для владельца)
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
def report_list(request):
    attempts = Attempt.objects.all()
    return render(request, 'report_list.html', {'attempts': attempts})
