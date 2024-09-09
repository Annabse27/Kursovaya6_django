"""
Конфигурация URL для проекта.

Этот файл содержит основные маршруты, включая маршруты для блога,
пользовательских страниц, рассылок и панели администратора.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views  # Импорт пользовательских представлений

# Основные маршруты приложения
urlpatterns = [
   path('admin/', admin.site.urls),
   path('users/', include('users.urls')),  # Маршруты для пользователей
   path('mailings/', core_views.mailing_list, name='mailing-list'),  # Список всех рассылок
   path('mailings/active/', core_views.active_mailings, name='active-mailings'),  # Активные рассылки
   path('clients/', core_views.client_list, name='client-list'),  # Список клиентов
   path('blog/', include('blog.urls')),  # Маршруты для блога
   path('accounts/', include('allauth.urls')),  # Аутентификация через allauth
   path('', core_views.home, name='home'),  # Главная страница
   path('manager/', core_views.manager_dashboard, name='manager_dashboard'),
   path('client_dashboard/', core_views.client_dashboard, name='client_dashboard'),
   path('admin_dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
   path('profile/', core_views.profile, name='profile'),
   path('mailings/create/', core_views.create_mailing, name='mailing-create'),  # Создание рассылки
   path('mailings/<int:mailing_id>/edit/', core_views.edit_mailing, name='mailing-edit'),  # Редактирование рассылки
   path('mailings/<int:mailing_id>/delete/', core_views.delete_mailing, name='mailing-delete'),  # Удаление рассылки
   path('admin/users/', core_views.admin_user_list, name='admin_user_list'),  # Управление пользователями
   path('manager/disable_mailing/<int:mailing_id>/', core_views.disable_mailing, name='disable_mailing'),
   path('manager/block_user/<int:client_id>/', core_views.block_user, name='block_user'),
]

# Подключение медиа-файлов в режиме отладки
if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
