from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from .models import BlogPost
from .forms import BlogPostForm, BlogPostUpdateForm
from .utils import get_blogpost_for_cache



class BlogPostListView(ListView):
    """Список опубликованных постов"""
    model = BlogPost
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        # Прямая фильтрация по базе данных для отладки
        return BlogPost.objects.filter(is_published=True)


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



class BlogPostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновление поста"""
    model = BlogPost
    form_class = BlogPostUpdateForm
    permission_required = 'blog.change_blogpost'
    template_name = 'blog/blog_form.html'

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:blog_detail', args=[self.kwargs.get('pk')])

class BlogPostDeleteView(PermissionRequiredMixin, DeleteView):
    """Удаление поста"""
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'  # Явно указываем правильное имя шаблона
    success_url = reverse_lazy('blog:blog_list')
    permission_required = 'blog.delete_blogpost'

