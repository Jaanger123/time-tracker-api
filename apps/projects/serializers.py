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


class TaskReadSerializer(serializers.ModelSerializer):
    task_type = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'name', 'task_type']

    def get_task_type(self, obj):
        return obj.task_type.id if obj.task_type else None


class TaskCreateSerializer(serializers.ModelSerializer):
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = ['id', 'name', 'task_type']


class ProjectSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    service_line = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_status(self, obj):
        return obj.status.name if obj.status else None

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_manager(self, obj):
        return obj.manager.email if obj.manager else None

    def get_client(self, obj):
        return obj.client.name if obj.client else None

    def get_department(self, obj):
        return obj.department.name if obj.department else None

    def get_service_line(self, obj):
        return obj.service_line.name if obj.service_line else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None


class ProjectCreateSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=ProjectStatus.objects.all(),
        required=False,
        allow_null=True,
    )
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True,
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=False,
        allow_null=True,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )
    service_line = serializers.PrimaryKeyRelatedField(
        queryset=ServiceLine.objects.all(),
        required=False,
        allow_null=True,
    )
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Project
        fields = '__all__'


class ProjectDetailSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='status.name')
    country = serializers.ReadOnlyField(source='country.code')
    manager = serializers.ReadOnlyField(source='manager.name')
    client = serializers.ReadOnlyField(source='client.name')
    department = serializers.ReadOnlyField(source='department.name')
    service_line = serializers.ReadOnlyField(source='service_line.name')
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'code',
            'description',
            'project_color',
            'is_chargeable',
            'status',
            'country',
            'manager',
            'client',
            'department',
            'service_line',
            'tasks',
        ]

    def get_tasks(self, obj):
        tasks = Task.objects.filter(task_type=obj.task_type)

        return TaskReadSerializer(tasks, many=True).data
