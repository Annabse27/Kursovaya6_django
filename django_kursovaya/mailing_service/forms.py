from django import forms
from .models import Client, Message, MailingSettings

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'name', 'comments']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['theme', 'body']

class MailingSettingsForm(forms.ModelForm):
   start_datetime = forms.DateTimeField(
       widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD HH:MM:SS'}, format='%Y-%m-%d %H:%M:%S'),
       label="Дата и время начала"
   )
   end_datetime = forms.DateTimeField(
       widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD HH:MM:SS'}, format='%Y-%m-%d %H:%M:%S'),
       label="Дата и время окончания"
   )

   class Meta:
       model = MailingSettings
       fields = ['start_datetime', 'end_datetime', 'periodicity', 'mailing_status', 'message', 'clients']
