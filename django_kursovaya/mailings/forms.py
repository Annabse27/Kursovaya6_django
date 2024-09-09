from django import forms
from .models import Mailing

class MailingForm(forms.ModelForm):
    """
    Форма для создания и редактирования рассылок.
    Использует модель Mailing и включает все ее поля.
    """
    class Meta:
        model = Mailing
        fields = '__all__'
