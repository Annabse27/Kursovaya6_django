from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mailings.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),  # Подключаем маршруты users
    path('', include('mailings.urls')),  # Подключаем маршруты mailings для главной страницы

    path('', home, name='home'),
    path('blog/', include('blog.urls', namespace='blog')),  # Подключение приложения блога
    #path('mailings/', include('mailings.urls', namespace='mailings')),  # Подключаем с namespace

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


