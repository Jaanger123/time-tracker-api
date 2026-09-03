from django.contrib.auth import get_user_model

from rest_framework import serializers

from common.utils import is_admin
from .models import *


User = get_user_model()


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'


class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStatus
        fields = ['id', 'name']


class ServiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLine
        fields = ['id', 'name']


class TaskTypeSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = TaskType
        fields = ['id', 'name', 'is_active', 'tasks']

    def get_tasks(self, obj):
        request = self.context.get('request')
        user = request.user

        tasks = Task.objects.filter(task_type=obj)

        if not is_admin(user):
            tasks = tasks.filter(is_active=True)

        return TaskReadSerializer(tasks, many=True).data


class TaskReadSerializer(serializers.ModelSerializer):
    task_type = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'name', 'is_active', 'task_type']

    def get_task_type(self, obj):
        return obj.task_type.id if obj.task_type else None


class TaskWriteSerializer(serializers.ModelSerializer):
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=True,
    )

    class Meta:
        model = Task
        fields = ['id', 'name', 'is_active', 'task_type']


class TaskImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class ProjectCodeReadSerializer(serializers.ModelSerializer):
    project = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCode
        fields = ['id', 'code', 'project', 'created_at']

    def get_project(self, obj):
        return obj.project.id if obj.project else None


class ProjectReadSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    service_line = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    codes = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'closed_date',
        ]

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

    def get_service_type(self, obj):
        return obj.service_type.name if obj.service_type else None

    def get_codes(self, obj):
        codes = ProjectCode.objects.filter(project=obj.id).order_by('created_at')

        return ProjectCodeReadSerializer(codes, many=True).data


class ProjectDetailSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='status.name')
    country = serializers.ReadOnlyField(source='country.code')
    manager = serializers.ReadOnlyField(source='manager.name')
    client = serializers.ReadOnlyField(source='client.name')
    department = serializers.ReadOnlyField(source='department.name')
    service_line = serializers.ReadOnlyField(source='service_line.name')
    service_type = serializers.ReadOnlyField(source='service_type.name')
    tasks = serializers.SerializerMethodField()
    codes = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'closed_date',
        ]

    def get_tasks(self, obj):
        tasks = Task.objects.filter(task_type=obj.task_type, is_active=True)

        return TaskReadSerializer(tasks, many=True).data

    def get_codes(self, obj):
        codes = ProjectCode.objects.filter(project=obj.id).order_by('created_at')

        return ProjectCodeReadSerializer(codes, many=True).data


class ProjectCreateSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(
        queryset=ProjectStatus.objects.all(),
        required=True,
    )
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=True,
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=True,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=True,
    )
    service_line = serializers.PrimaryKeyRelatedField(
        queryset=ServiceLine.objects.all(),
        required=True,
    )
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=True,
    )
    service_type = serializers.PrimaryKeyRelatedField(
        queryset=ServiceType.objects.all(),
        required=True,
    )

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'closed_date',
        ]
