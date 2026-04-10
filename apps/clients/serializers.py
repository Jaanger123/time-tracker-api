from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.projects.serializers import ProjectReadSerializer
from .models import Client, Sector


User = get_user_model()


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    sector = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = '__all__'

    def get_sector(self, obj):
        return obj.sector.name if obj.sector else None


class ClientDetailSerializer(serializers.ModelSerializer):
    projects = ProjectReadSerializer(source='project_set', many=True, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'


class ClientCreateSerializer(serializers.ModelSerializer):
    sector = serializers.PrimaryKeyRelatedField(
        queryset=Sector.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Client
        fields = '__all__'