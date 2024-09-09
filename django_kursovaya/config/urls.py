"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views  # Импорт представления home
from core.views import (client_dashboard, manager_dashboard,
                        admin_dashboard, profile, mailing_list,
                        active_mailings, client_list)


from django.urls import path
from core import views as core_views  # Импорт представления home
from core.views import disable_mailing, block_user
from allauth.account.views import LogoutView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('mailings/', core_views.mailing_list, name='mailing-list'),  # Список всех рассылок
    path('mailings/active/', core_views.active_mailings, name='active-mailings'),  # Активные рассылки
    path('clients/', core_views.client_list, name='client-list'),  # Список клиентов
    path('blog/', include('blog.urls')),  # Подключение блога
    path('accounts/', include('allauth.urls')),  # Авторизация через allauth
    path('', core_views.home, name='home'),  # Главная страница
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('client_dashboard/', core_views.client_dashboard, name='client_dashboard'),
    path('admin_dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    path('profile/', core_views.profile, name='profile'),
    path('mailings/create/', core_views.create_mailing, name='mailing-create'),  # Создание рассылки
    path('mailings/<int:mailing_id>/edit/', core_views.edit_mailing, name='mailing-edit'),  # Редактирование рассылки
    path('mailings/<int:mailing_id>/delete/', core_views.delete_mailing, name='mailing-delete'),  # Удаление рассылки
    path('admin/users/', core_views.admin_user_list, name='admin_user_list'),
    path('manager/disable_mailing/<int:mailing_id>/', disable_mailing, name='disable_mailing'),
    path('manager/block_user/<int:client_id>/', block_user, name='block_user'),
    #path('accounts/logout/', LogoutView.as_view(), name='account_logout'),  # Выход через allauth

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
