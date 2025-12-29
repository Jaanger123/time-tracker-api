from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *


User = get_user_model()


class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = ['id', 'name']


class ServiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLine
        fields = ['id', 'name']


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    task_type = serializers.ReadOnlyField(source='task_type.name')

    class Meta:
        model = Task
        fields = ['id', 'name', 'task_type']


class ProjectSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='status.name')
    country = serializers.ReadOnlyField(source='country.code')
    manager = serializers.ReadOnlyField(source='manager.name')
    client = serializers.ReadOnlyField(source='client.name')
    department = serializers.ReadOnlyField(source='department.name')
    service_line = serializers.ReadOnlyField(source='service_line.name')
    task_type = serializers.ReadOnlyField(source='task_type.code')

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'code',
            'description',
            'is_chargeable',
            'status',
            'country',
            'manager',
            'client',
            'department',
            'service_line',
            'task_type',
        ]