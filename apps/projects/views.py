from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import *
from .models import *


class ProjectStatusViewSet(ModelViewSet):
    queryset = ProjectStatus.objects.all()
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]


class ServiceLineViewSet(ModelViewSet):
    queryset = ServiceLine.objects.all()
    serializer_class = ServiceLineSerializer
    permission_classes = [IsAuthenticated]


class TaskTypeViewSet(ModelViewSet):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated]


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all().select_related(
        'task_type'
    )
    serializer_class = TaskReadSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def internal(self, request):
        tasks = Task.objects.filter(task_type__name='Internal')
        serializer = TaskReadSerializer(tasks, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leave(self, request):
        tasks = Task.objects.filter(task_type__name='Leave')
        serializer = TaskReadSerializer(tasks, many=True)

        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TaskReadSerializer

        return TaskCreateSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all().select_related(
        'status', 
        'country', 
        'manager', 
        'client', 
        'department', 
        'service_line',
        'task_type'
    )
    serializer_class = ProjectReadSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.action == 'retrieve':
                return ProjectDetailSerializer

            return ProjectReadSerializer

        return ProjectCreateSerializer
