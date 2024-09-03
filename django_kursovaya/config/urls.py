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
from core.views import client_dashboard, manager_dashboard, admin_dashboard, profile


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('mailings/', include('mailings.urls')),
    path('blog/', include('blog.urls')),
    path('api/', include('mailings.urls')),  # Подключаем API
    path('accounts/', include('allauth.urls')),  # Allauth URL
    path('', core_views.home, name='home'),  # Маршрут для главной страницы
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('client_dashboard/', client_dashboard, name='client_dashboard'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('profile/', profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
