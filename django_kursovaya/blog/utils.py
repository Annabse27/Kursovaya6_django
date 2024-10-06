#А точнее кеширование

from django.core.cache import cache
from .models import BlogPost
from django.conf import settings


def get_blogpost_for_cache():
    """Получает опубликованные посты из кэша или БД и записывает в кэш при необходимости"""
    if settings.CACHE_ENABLED:
        key = 'blogposts'
        blogposts_list = cache.get(key)
        if blogposts_list is None:
            blogposts_list = BlogPost.objects.filter(is_published=True)
            cache.set(key, blogposts_list)
    else:
        blogposts_list = BlogPost.objects.filter(is_published=True)
    return blogposts_list
