from django.forms import ModelForm
from .models import BlogPost

class BlogPostForm(ModelForm):
    """Форма для создания нового поста"""
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'preview']

class BlogPostUpdateForm(ModelForm):
    """Форма для обновления существующего поста"""
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'preview', 'is_published']
