from django.contrib.auth import get_user_model

from rest_framework import serializers
from apps.accounts.models import Country

from apps.projects.serializers import ProjectReadSerializer
from .models import *


User = get_user_model()


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'


class PieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pie
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    sector = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    pie = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = '__all__'

    def get_sector(self, obj):
        return obj.sector.name if obj.sector else None

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_pie(self, obj):
        return obj.pie.name if obj.pie else None


class ClientDetailSerializer(serializers.ModelSerializer):
    projects = ProjectReadSerializer(source='project_set', many=True, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'


class ClientCreateSerializer(serializers.ModelSerializer):
    sector = serializers.PrimaryKeyRelatedField(
        queryset=Sector.objects.all(),
        required=True,
    )
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=True,
    )
    pie = serializers.PrimaryKeyRelatedField(
        queryset=Pie.objects.all(),
        required=True,
    )

    class Meta:
        model = Client
        fields = '__all__'
