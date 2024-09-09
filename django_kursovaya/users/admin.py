from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Нужно указать здесь поля, которые будут отображаться в админке
    list_display = ('username', 'email', 'is_staff', 'is_active', 'phone_number')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
