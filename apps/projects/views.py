from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from django.db.models import OuterRef, Subquery, F

from django_filters.rest_framework import DjangoFilterBackend

from apps.projects.pagination import ProjectPagination
from .filters import ProjectFilter
from utils import generate_excel
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
        'country_of_ubo', 
        'manager', 
        'client', 
        'department', 
        'service_line',
        'task_type'
    ).order_by('id')
    serializer_class = ProjectReadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProjectPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProjectFilter
    ordering_fields = ['code', 'client_name', 'manager_email', 'country_code', 'country_of_ubo_code', 'department_name']

    def _export_excel(self, queryset):
        columns = [
            'code',
            'description',
            'entity',
            'ic',
            'client_name',
            'country_code',
            'country_of_ubo_code',
            'is_chargeable',
            'is_code_recurring',
            'status_name',
            'manager_email',
            'department_name',
            'service_line_name',
            'task_type_name',
            'service_type_name',
            'agreement_date',
        ]

        headers = [
            'Code',
            'Description',
            'Entity',
            'IC',
            'Client Name',
            'Country',
            'Country of UBO',
            'Is Chargeable',
            'Is Code Reccuring',
            'Status',
            'Manager',
            'Department',
            'Service Line',
            'Task Type',
            'Service Type',
            'Agreement Date',
        ]

        return generate_excel(queryset, 'Projects', columns, headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        export_type = request.query_params.get('export')

        if export_type == 'excel':
            return self._export_excel(queryset)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

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
            country_of_ubo_code=F('country_of_ubo__code'),
            department_name=F('department__name'),
            status_name=F('status__name'),
            service_line_name=F('service_line__name'),
            task_type_name=F('task_type__name'),
            service_type_name=F('service_type__name'),
            code=Subquery(latest_code_subquery)
        )
