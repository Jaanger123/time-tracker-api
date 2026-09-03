from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from django.db.models import OuterRef, Subquery, F
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend

from apps.projects.pagination import ProjectPagination
from common.mixins import AdminWritePermissionMixin
from common.utils import generate_excel, is_admin
from common.permissions import IsAdminRole
from .utils import export_tasks, import_tasks
from .filters import ProjectFilter
from .serializers import *
from .models import *


class ServiceTypeViewSet(ModelViewSet, AdminWritePermissionMixin):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ProjectStatusViewSet(ModelViewSet, AdminWritePermissionMixin):
    queryset = ProjectStatus.objects.all()
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ServiceLineViewSet(ModelViewSet, AdminWritePermissionMixin):
    queryset = ServiceLine.objects.all()
    serializer_class = ServiceLineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class TaskTypeViewSet(ModelViewSet, AdminWritePermissionMixin):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        queryset = TaskType.objects.all()

        if not is_admin(self.request.user):
            queryset = queryset.filter(is_active=True)

        return queryset

    @action(detail=True, methods=['get'], url_path='export-excel')
    def export_excel(self, request, pk=None):
        task_type = self.get_object()

        excel = export_tasks(task_type)

        response = HttpResponse(
            excel,
            content_type=(
                'application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.sheet'
            ),
        )

        response['Content-Disposition'] = (
            f'attachment; filename={task_type.name}.xlsx'
        )

        return response

    @action(detail=True, methods=['post'], url_path='import-excel')
    def import_excel(self, request, pk=None):
        serializer = TaskImportSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        task_type = self.get_object()

        import_tasks(
            task_type=task_type,
            file=serializer.validated_data['file'],
        )

        return Response({
            'message': 'Tasks imported successfully.'
        })


class TaskViewSet(ModelViewSet, AdminWritePermissionMixin):
    queryset = Task.objects.all()
    serializer_class = TaskReadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Task.objects.select_related(
            'task_type'
        )

        if not is_admin(self.request.user):
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TaskReadSerializer

        return TaskWriteSerializer

    @action(detail=False, methods=['get'])
    def internal(self, request):
        tasks = self.get_queryset().filter(task_type__name='Internal')
        serializer = TaskReadSerializer(tasks, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leave(self, request):
        tasks = self.get_queryset().filter(task_type__name='Leave')
        serializer = TaskReadSerializer(tasks, many=True)

        return Response(serializer.data)


class ProjectViewSet(ModelViewSet, AdminWritePermissionMixin):
    queryset = Project.objects.all().select_related(
        'status', 
        'country', 
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
    ordering_fields = ['code', 'client_name', 'manager_email', 'country_code', 'department_name']

    def _export_excel(self, queryset):
        columns = [
            'code',
            'description',
            'entity',
            'ic',
            'client_name',
            'country_code',
            'is_chargeable',
            'is_code_recurring',
            'status_name',
            'manager_email',
            'department_name',
            'service_line_name',
            'task_type_name',
            'service_type_name',
            'agreement_date',
            'closed_date',
        ]

        headers = [
            'Code',
            'Description',
            'Entity',
            'IC',
            'Client Name',
            'Country',
            'Is Chargeable',
            'Is Code Reccuring',
            'Status',
            'Manager',
            'Department',
            'Service Line',
            'Task Type',
            'Service Type',
            'Agreement Date',
            'Closed Date',
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
        latest_code_subquery = ProjectCode.objects.filter(
            project=OuterRef('pk')
        ).order_by('-created_at').values('code')[:1]

        return Project.objects.annotate(
            client_name=F('client__name'),
            manager_email=F('manager__email'),
            country_code=F('country__code'),
            department_name=F('department__name'),
            status_name=F('status__name'),
            service_line_name=F('service_line__name'),
            task_type_name=F('task_type__name'),
            service_type_name=F('service_type__name'),
            code=Subquery(latest_code_subquery)
        )
