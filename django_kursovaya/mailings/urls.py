from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('', views.home, name='home'),  # Убедитесь, что хотя бы один маршрут здесь есть
    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('client/create/', views.ClientCreateView.as_view(), name='create_client'),
    path('client/<int:pk>/', views.ClientDetailView.as_view(), name='view_client'),
    path('client/<int:pk>/update/', views.ClientUpdateView.as_view(), name='update_client'),
    path('client/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='delete_client'),

    path('messages/', views.MessageListView.as_view(), name='messages'),
    path('message/create/', views.MessageCreateView.as_view(), name='create_message'),
    path('message/<int:pk>/', views.MessageDetailView.as_view(), name='view_message'),
    path('message/<int:pk>/update/', views.MessageUpdateView.as_view(), name='update_message'),
    path('message/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='delete_message'),

    path('settings/', views.MailingSettingsListView.as_view(), name='settings'),
    path('setting/create/', views.MailingSettingsCreateView.as_view(), name='create_setting'),
    path('setting/<int:pk>/', views.MailingSettingsDetailView.as_view(), name='view_setting'),
    path('setting/<int:pk>/update/', views.MailingSettingsUpdateView.as_view(), name='update_setting'),
    path('setting/<int:pk>/delete/', views.MailingSettingsDeleteView.as_view(), name='delete_setting'),

    path('attempts/', views.MailingAttemptListView.as_view(), name='attempts'),

    path('reports/', views.ReportView.as_view(), name='report'),  # Указываем маршрут для отчёта


]
