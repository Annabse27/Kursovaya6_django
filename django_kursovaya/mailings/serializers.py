"""
Сериализаторы для преобразования данных моделей в формат JSON, используемый в API.
"""
from rest_framework import serializers
from .models import Client, Message, Mailing, Attempt

class ClientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Client, включает все поля.
    """
    class Meta:
        model = Client
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Message, включает все поля.
    """
    class Meta:
        model = Message
        fields = '__all__'

class MailingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Mailing, включает все поля.
    """
    class Meta:
        model = Mailing
        fields = '__all__'

class AttemptSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Attempt, включает все поля.
    """
    class Meta:
        model = Attempt
        fields = '__all__'
