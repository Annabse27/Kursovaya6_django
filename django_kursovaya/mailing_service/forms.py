from django import forms
from .models import Client, Message, MailingSettings
from datetime import datetime


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'name', 'comments', 'is_active']  # Добавляем поле is_active

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['theme', 'body']


class MailingSettingsForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}),
        label="Дата начала"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM'}),
        label="Время начала"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}),
        label="Дата окончания"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM'}),
        label="Время окончания"
    )


    class Meta:
        model = MailingSettings
        fields = ['start_date', 'start_time', 'end_date', 'end_time', 'periodicity', 'mailing_status', 'message', 'clients']


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        start_time = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")


        # Объединяем дату и время
        if start_date and start_time:
            cleaned_data['start_datetime'] = datetime.combine(start_date, start_time)
        if end_date and end_time:
            cleaned_data['end_datetime'] = datetime.combine(end_date, end_time)


        return cleaned_data
