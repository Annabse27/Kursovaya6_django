from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from django.shortcuts import redirect

@receiver(user_logged_in)
def redirect_user_after_login(sender, request, user, **kwargs):
    if user.groups.filter(name='Admin').exists():
        return redirect('/admin_dashboard/')
    elif user.groups.filter(name='Manager').exists():
        return redirect('/manager_dashboard/')
    elif user.groups.filter(name='Client').exists():
        return redirect('/client_dashboard/')
    else:
        return redirect('/')  # на случай, если у пользователя нет группы
