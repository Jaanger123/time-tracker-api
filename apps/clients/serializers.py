from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Client


User = get_user_model()


class ClientSerializer(serializers.ModelSerializer):
    manager = serializers.ReadOnlyField(source='manager.name')
    sector = serializers.ReadOnlyField(source='sector.name')

    class Meta:
        model = Client
        fields = [
            'id',
            'name',
            'group',
            'personal_number',
            'sector',
            'manager',
        ]