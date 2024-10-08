from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from .models import BlogPost
from .forms import BlogPostForm, BlogPostUpdateForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin


class BlogPostListView(ListView):
    """Список опубликованных постов"""
    model = BlogPost
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Добавляем переменные для проверки прав в шаблоне
        context['is_manager'] = user.groups.filter(name='Manager').exists()
        context['is_superuser'] = user.is_superuser
        return context


class BlogPostDetailView(DetailView):
    """Детальная страница поста"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        post.views_count += 1
        post.save(update_fields=['views_count'])
        return post

class BlogPostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        form.instance.is_published = True  # По умолчанию публикуем статьи
        return super().form_valid(form)



class BlogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление поста"""
    model = BlogPost
    form_class = BlogPostUpdateForm
    template_name = 'blog/blog_form.html'

    def test_func(self):
        # Проверка прав на редактирование
        post = self.get_object()
        user = self.request.user
        # Пользователь может редактировать, если он автор, администратор или менеджер
        return user == post.author or user.is_superuser or user.has_perm('blog.change_blogpost')

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:blog_detail', args=[self.kwargs.get('pk')])


class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление поста"""
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')

    def test_func(self):
        # Проверка прав на удаление
        post = self.get_object()
        user = self.request.user
        # Пользователь может удалить, если он автор, администратор или менеджер
        return user == post.author or user.is_superuser or user.has_perm('blog.delete_blogpost')

    '''def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        # Проверка прав: автор поста, администратор или менеджер
        if post.author != request.user and not (
                request.user.is_superuser or request.user.has_perm('blog.delete_blogpost')):
            raise PermissionDenied("У вас нет прав для удаления этого поста.")
        return super().dispatch(request, *args, **kwargs)
'''