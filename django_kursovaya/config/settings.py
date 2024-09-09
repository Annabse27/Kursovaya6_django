"""
Настройки Django для проекта.

Этот файл включает настройки, пути и переменные окружения для работы
с проектом. Все настройки производятся через файл .env, за исключением
некоторых стандартных значений.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Базовый путь к проекту
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из файла .env
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path)

# Основные настройки безопасности
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback_secret_key')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# Подключенные приложения
INSTALLED_APPS = [
   'django.contrib.admin',
   'django.contrib.auth',
   'django.contrib.contenttypes',
   'django.contrib.sessions',
   'django.contrib.messages',
   'django.contrib.staticfiles',
   'django.contrib.sites',  # Необходимо для allauth
   'core',  # Важные пользовательские приложения
   'users',
   'mailings',
   'blog',
   'rest_framework',  # Подключение REST API
   'allauth',  # Приложение для аутентификации
   'allauth.account',
   'allauth.socialaccount',
   'allauth.socialaccount.providers.google',
   'allauth.socialaccount.providers.github',
]

# Идентификатор сайта для django.contrib.sites
SITE_ID = 1

# Бэкенды аутентификации
AUTHENTICATION_BACKENDS = (
   'django.contrib.auth.backends.ModelBackend',
   'allauth.account.auth_backends.AuthenticationBackend',
)

# Модель пользователя
AUTH_USER_MODEL = 'users.CustomUser'

# URL-адреса перенаправления после входа/выхода
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGOUT_ON_GET = False  # Корректный выход

# Middleware для обработки запросов
MIDDLEWARE = [
   'django.middleware.security.SecurityMiddleware',
   'django.contrib.sessions.middleware.SessionMiddleware',
   'django.middleware.common.CommonMiddleware',
   'django.middleware.csrf.CsrfViewMiddleware',
   'django.contrib.auth.middleware.AuthenticationMiddleware',
   'django.contrib.messages.middleware.MessageMiddleware',
   'django.middleware.clickjacking.XFrameOptionsMiddleware',
   'allauth.account.middleware.AccountMiddleware',
]

# Основные пути и шаблоны
ROOT_URLCONF = 'config.urls'
TEMPLATES = [
   {
       'BACKEND': 'django.template.backends.django.DjangoTemplates',
       'DIRS': [BASE_DIR / 'templates'],  # Директория для шаблонов
       'APP_DIRS': True,
       'OPTIONS': {
           'context_processors': [
               'django.template.context_processors.debug',
               'django.template.context_processors.request',
               'django.contrib.auth.context_processors.auth',
               'django.contrib.messages.context_processors.messages',
           ],
       },
   },
]

# Настройки базы данных (используется PostgreSQL)
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': os.getenv('DATABASE_NAME'),
       'USER': os.getenv('DATABASE_USER'),
       'PASSWORD': os.getenv('DATABASE_PASSWORD'),
       'HOST': os.getenv('DATABASE_HOST'),
       'PORT': os.getenv('DATABASE_PORT'),
   }
}

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
   {
       'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
   },
   {
       'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
   },
   {
       'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
   },
   {
       'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
   },
]

# Настройки интернационализации
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Настройки для статических и медиа-файлов
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Путь для собранных статических файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Конфигурация Redis для кэширования
CACHES = {
   'default': {
       'BACKEND': 'django_redis.cache.RedisCache',
       'LOCATION': 'redis://127.0.0.1:6379/1',  # Локальный Redis
       'OPTIONS': {
           'CLIENT_CLASS': 'django_redis.client.DefaultClient',
       },
       'KEY_PREFIX': 'myproject'
   }
}
CACHE_TTL = 60 * 15  # Время жизни кэша (15 минут)

"""
# Настройка провайдеров (социальных сетей) для учетной записи
SOCIALACCOUNT_PROVIDERS = {
   'google': {
       'SCOPE': [
           'profile',
           'email',
       ],
       'AUTH_PARAMS': {
           'access_type': 'offline',
       }
   },
   'github': {
       'SCOPE': [
           'user',
           'repo',
           'read:org',
       ],
   },
}
"""
