from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from django.db.models import OuterRef, Subquery, F

from django_filters.rest_framework import DjangoFilterBackend

from apps.projects.pagination import ProjectPagination
from .filters import ProjectFilter
from .serializers import *
from .models import *


latest_code_subquery = ProjectCode.objects.filter(
    project=OuterRef('pk')
).order_by('-created_at').values('code')[:1]


class ServiceTypeViewSet(ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ProjectStatusViewSet(ModelViewSet):
    queryset = ProjectStatus.objects.all()
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ServiceLineViewSet(ModelViewSet):
    queryset = ServiceLine.objects.all()
    serializer_class = ServiceLineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class TaskTypeViewSet(ModelViewSet):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all().select_related(
        'task_type'
    )
    serializer_class = TaskReadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

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
    pagination_class = ProjectPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProjectFilter
    ordering_fields = ['code', 'client_name', 'manager_email', 'country_code', 'department_name']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.action == 'retrieve':
                return ProjectDetailSerializer

            return ProjectReadSerializer

        return ProjectCreateSerializer

    def get_queryset(self):
        return Project.objects.annotate(
            client_name=F('client__name'),
            manager_email=F('manager__email'),
            country_code=F('country__code'),
            department_name=F('department__name'),
            code=Subquery(latest_code_subquery)
        )
