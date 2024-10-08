from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Настраиваем Django настройки для использования с Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('config')

# Используем настройки Django в Celery
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в каждом установленном приложении
celery_app.autodiscover_tasks()


