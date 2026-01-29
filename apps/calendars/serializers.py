from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *


User = get_user_model()


class TimeEntryUserSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    project_color = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        exclude = ['user']

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_client(self, obj):
        return obj.client.name if obj.client else None

    def get_project(self, obj):
        return obj.project.name if obj.project else None

    def get_project_color(self, obj):
        return obj.project.project_color if obj.project else None

    def get_project_code(self, obj):
        return obj.project.code if obj.project else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None

    def get_task(self, obj):
        return obj.task.name if obj.task else None


class TimeEntryAdminSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    project_color = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = '__all__'

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_client(self, obj):
        return obj.client.name if obj.client else None

    def get_project(self, obj):
        return obj.project.name if obj.project else None

    def get_project_color(self, obj):
        return obj.project.project_color if obj.project else None

    def get_project_code(self, obj):
        return obj.project.code if obj.project else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None

    def get_task(self, obj):
        return obj.task.name if obj.task else None


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True,
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=False,
        allow_null=True,
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False,
        allow_null=True,
    )
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=False,
        allow_null=True,
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = TimeEntry
        exclude = ['user']