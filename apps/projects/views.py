from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

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
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class ProjectListView(ListAPIView):
    queryset = Project.objects.all().select_related(
        'status', 
        'country', 
        'manager', 
        'client', 
        'department', 
        'service_line',
        'task_type'
    )
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]