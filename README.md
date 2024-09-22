### README для проекта рассылок (Курсовая работа 6 Django)

## Описание проекта

Проект представляет собой веб-приложение для управления рассылками и администрирования пользователей. Пользователи могут создавать, редактировать и удалять рассылки, управлять клиентами, просматривать отчеты по рассылкам и блокировать пользователей. Проект реализует систему управления доступом на основе ролей: администраторы, менеджеры и клиенты имеют разные права.

## Основные функции

1. **Управление рассылками (CRUD)**
   - Создание, редактирование, просмотр, удаление рассылок.
   - Управление клиентами и сообщениями для рассылок.
2. **Система ролей и прав доступа**
   - Администраторы могут управлять пользователями и рассылками.
   - Менеджеры могут просматривать рассылки и блокировать пользователей.
   - Клиенты могут просматривать свои рассылки.
3. **Интеграция с блогом**
   - Поддержка создания и управления статьями для блога.
4. **Автоматическая отправка рассылок**
   - Использование библиотеки `django-apscheduler` для периодических задач.
5. **Кэширование с использованием Redis**
   - Реализовано для оптимизации отображения данных блога и статистики на главной странице.
6. **Формы для управления данными**
   - Используются Django Forms для создания и редактирования рассылок, сообщений и клиентов.
7. **Регистрация и авторизация через `django-allauth`**
   - Реализована регистрация пользователей, авторизация и подтверждение email с помощью `django-allauth`. Это упрощает управление учетными записями и поддерживает верификацию через email.

## Структура проекта

```
django_kursovaya/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── users/
│   ├── fixtures/
│   │   └── initial_data.json
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── mailings/
│   ├── management/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── blog/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── account/
│   ├── blog/
│   ├── clients/
│   ├── mailings/
│   ├── admin_dashboard.html
│   ├── admin_user_list.html
│   ├── base_generic.html
│   ├── client_dashboard.html
│   ├── home.html
│   ├── mailing_form.py
│   ├── manager_dashboard.html
│   └── report_list.html
├── media/
├── static/
├── manage.py
└── .env
```

## Установка и запуск проекта

### 1. Клонирование репозитория
```
git clone https://github.com/Annabse27/Kursovaya6_django/
cd django_kursovaya
```

### 2. Установка зависимостей
Убедитесь, что у вас установлены `Python 3.8+`, `PostgreSQL`, `Redis`, и `Docker`. Настройте виртуальное окружение и установите зависимости:

```
poetry shell
poetry install
```

### 3. Настройка базы данных
Настройте PostgreSQL, добавив параметры в `.env` файл:
```
DJANGO_SECRET_KEY="your_DJANGO_SECRET_KEY"
DJANGO_DEBUG="True"
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

# Настройки базы данных
DATABASE_NAME="your_db_name"
DATABASE_USER="your_db_user"
DATABASE_PASSWORD="your_db_password"
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Используемый URL для API
API_BASE_URL=https://api.example.com

# Настройки Redis
REDIS_URL=redis://localhost:6379/0

# Настройки почтового сервера (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com  # SMTP сервер провайдера
EMAIL_PORT=587  # или 465, в зависимости от провайдера
EMAIL_USE_TLS=True  # или False, если используется SSL
EMAIL_USE_SSL=False  # или True, если используется SSL
EMAIL_HOST_USER="your_email"  # email
EMAIL_HOST_PASSWORD="email_password"  # Пароль от email
DEFAULT_FROM_EMAIL="your_email"  # Email, который будет указан как отправитель
```

Примените миграции:
```
python manage.py migrate
```

### 4. Загрузка данных (фикстуры)
```
python manage.py loaddata users/fixtures/initial_data.json
```

### 5. Запуск сервера
Запустите Redis через Docker:
```
docker run -d --name redis-server -p 6379:6379 redis
docker ps -a
docker start redis-server
```

Затем запустите сервер Django:
```
python manage.py runserver
```

### 6. Запуск планировщика задач
Запустите `django-apscheduler` для обработки рассылок:
```
python manage.py runapscheduler
```

## Основные страницы приложения

- `/accounts/signup/`: Регистрация пользователя (реализована через `django-allauth`)
- `/accounts/login/`: Авторизация пользователя (реализована через `django-allauth`)
- `/mailings/`: Список рассылок, управление ими (CRUD)
- `/blog/`: Просмотр статей блога

## Особенности реализации

### 1. **Роли и права доступа**
- Администратор: полный доступ к рассылкам и управлению пользователями.
- Менеджер: может просматривать рассылки и блокировать пользователей, но не редактировать рассылки.
- Клиент: может просматривать свои рассылки.

### 2. **Использование `django-allauth`**
Для управления регистрацией и авторизацией пользователей используется библиотека `django-allauth`. Она обеспечивает готовый функционал для работы с пользователями, включая:
- Регистрация пользователей.
- Верификация email через отправку письма.
- Авторизация.
- Сброс пароля.

### 3. **Использование APScheduler**
Используется для автоматической отправки рассылок по расписанию.

### 4. **Кэширование с использованием Redis**
Часть данных блога и статистики на главной странице кешируется для ускорения работы приложения.

## Примечание
- Проект выложен на GitHub: [Ссылка на репозиторий](https://github.com/yourusername/django_kursovaya)
- Для полноценного использования проекта все конфиденциальные данные (такие как ключи API и параметры базы данных) вынесены в файл `.env`.

### Возможные референсы:
- Сервис похож на такие платформы, как **Mailchimp**, однако проект создавался для обучения и освоения основных функций рассылки и управления пользователями.
