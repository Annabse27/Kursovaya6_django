from django.db import models
from django.conf import settings

NULLABLE = {'blank': True, 'null': True}


class BlogPost(models.Model):
    title = models.CharField(max_length=150, verbose_name='Заголовок', help_text='Введите заголовок')
    slug = models.CharField(max_length=150, verbose_name='slug', **NULLABLE)
    content = models.TextField(verbose_name='Содержимое', help_text='Введите содержимое', **NULLABLE)
    preview = models.ImageField(upload_to='blog/', verbose_name='Превью', help_text="Загрузите превью", **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано', help_text='Опубликовать блог?')
    views_count = models.IntegerField(default=0, verbose_name='Просмотры', editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Автор', on_delete=models.SET_NULL, null=True,
                               blank=True)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Блоговая запись"
        verbose_name_plural = "Блоговые записи"
        ordering = ('-created_at',)  # Упорядочиваем по дате создания, от новых к старым
