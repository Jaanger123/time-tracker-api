from collections import defaultdict

from datetime import datetime

from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import openpyxl

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.db.models import Sum, Max, Q, F, OuterRef, Subquery
from django.http import HttpResponse

from .utils import get_working_days_list, get_country
from apps.projects.models import ProjectCode
from .permissions import IsOwnerOrAdmin
from .serializers import *
from .models import *


class CountrySettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        country, error = get_country(request)

        if error:
            return error

        settings = CountrySettings.get_settings(country.id)
        serializer = CountrySettingsSerializer(settings)

        return Response(serializer.data)

    def patch(self, request):
        country, error = get_country(request)

        if error:
            return error

        settings = CountrySettings.get_settings(country.id)
        serializer = CountrySettingsSerializer(
            settings,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        country, error = get_country(request)

        if error:
            return error

        settings = CountrySettings.get_settings(country.id)
        serializer = CountrySettingsSerializer(settings, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeEntryViewSet(ModelViewSet):
    queryset = TimeEntry.objects.all().select_related(
        'user',
        'country',
        'client',
        'project_code',
        'task_type',
        'task'
    )
    serializer_class = TimeEntryReadSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def _generate_excel(self, queryset):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Timesheet Report'

        columns = [
            'date',
            'user_email',
            'country_code',
            'user_department',
            'position',
            'detailed_grade',
            'hours',
            'project_department',
            'client_name',
            'project_code',
            'project_service_line',
            'task_type_name',
            'task_name',
            'description',
        ]

        headers = [
            'Date',
            'User Email',
            'Country',
            'User Department',
            'Position',
            'Grade',
            'Hours',
            'Project Department',
            'Client',
            'Project Code',
            'Service Line',
            'Task Type',
            'Task',
            'Description',
        ]

        sheet.append(headers)

        for col in range(1, len(headers) + 1):
            sheet.cell(row=1, column=col).font = Font(bold=True)

        for row in queryset:
            sheet.append([row.get(col) for col in columns])

        for column_cells in sheet.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=timesheet_report.xlsx'

        workbook.save(response)
        return response

    @action(detail=False, methods=['get'])
    def report(self, request):
        queryset = (
            TimeEntry.objects
            .select_related(
                'user',
                'country',
                'client',
                'project_code',
                'task_type',
                'task'
            )
            .annotate(
                user_email=F('user__email'),
                country_code=F('country__code'),
                user_department=F('user__department__name'),
                position=F('user__position__name'),
                detailed_grade=F('user__grade__name'),
                client_name=F('client__name'),
                project_department=F('project_code__project__department__name'),
                code=F('project_code__code'),
                project_service_line=F('project_code__project__service_line__name'),
                task_type_name=F('task_type__name'),
                task_name=F('task__name'),
            )
            .values(
                'date',
                'user_email',
                'country_code',
                'user_department',
                'position',
                'detailed_grade',
                'hours',
                'project_department',
                'client_name',
                'code',
                'project_service_line',
                'task_type_name',
                'task_name',
                'description',
            )
            .order_by('user_email', 'date')
        )

        format_type = request.query_params.get('export', 'json')

        if format_type == 'excel':
            return self._generate_excel(queryset)

        return Response(list(queryset))

    @action(detail=False, methods=['get'])
    def monitoring(self, request):
        country_id = request.query_params.get('country_id')
        settings = CountrySettings.get_settings(country_id)
        daily_hours = settings.hours_per_day
        working_days = set(settings.working_days)

        start_date = datetime.strptime(request.query_params.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.query_params.get('end_date'), '%Y-%m-%d').date()

        queryset = (
            User.objects
            .filter(
                country=country_id
            )
            .annotate(
                total_hours=Sum(
                    'time_entries__hours',
                    filter=Q(time_entries__date__range=(start_date, end_date))
                ),
                last_updated=Max(
                    'time_entries__updated_at',
                    filter=Q(time_entries__date__range=(start_date, end_date))
                )
            )
            .values(
                user_email=F('email'),
                user_id=F('id'),
                total_hours=F('total_hours'),
                last_updated=F('last_updated'),
            )
            .order_by('email')
        )

        time_entries = (
            TimeEntry.objects
            .filter(
                user__country=country_id,
                date__range=(start_date, end_date)
            )
            .values(
                'user_id', 
                'date'
            )
            .annotate(
                total_hours=Sum('hours')
            )
        )

        entries_by_user = defaultdict(dict)

        for row in time_entries:
            entries_by_user[row['user_id']][row['date']] = row['total_hours']

        working_days_list = get_working_days_list(start_date, end_date, country_id, working_days)
        required_hours = len(working_days_list) * daily_hours
        data = []

        for row in queryset:
            user_id = row['user_id']
            user_entries = entries_by_user.get(user_id, {})

            missing_days = []

            for day in working_days_list:
                hours = user_entries.get(day, 0)

                if hours < daily_hours:
                    missing_days.append({
                        'date': day,
                        'worked_hours': hours,
                        'missing_hours': daily_hours - hours
                    })

            if row['total_hours'] is None:
                row['total_hours'] = 0

            row['missing_days'] = missing_days
            row['missing_days_count'] = len(missing_days)
            total = row['total_hours']

            completion = (total / required_hours) if required_hours > 0 else 0

            row['required_hours'] = required_hours
            row['completion'] = round(completion * 100, 2)

            data.append(row)

        return Response(data)

    def get_serializer_class(self):
        user = self.request.user

        if self.action in ['list', 'retrieve']:
            if user.is_staff:
                return TimeEntryAdminReadSerializer

            return TimeEntryReadSerializer

        return TimeEntryCreateSerializer

    def get_queryset(self):
        user = self.request.user

        base_queryset = TimeEntry.objects.select_related(
            'country',
            'client',
            'project_code',
            'task_type',
            'task',
        )

        if user.is_staff:
            return base_queryset

        return base_queryset.filter(user=user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}



class CalendarViewSet(ModelViewSet):
    queryset = Calendar.objects.all().select_related(
        'country',
    )
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='day-types')
    def day_types(self, request):
        return Response({
            'day_types': [
                {
                    'value': value, 
                    'label': label
                }
                for value, label in Calendar.DayType.choices
            ]
        })

    @action(detail=False, methods=['get'])
    def holidays(self, request):
        user = request.user

        filtered_queryset = Calendar.objects.filter(day_type=Calendar.DayType.HOLIDAY)

        if not user.is_staff:
            filtered_queryset = filtered_queryset.filter(country=user.country.id)

        serializer = self.get_serializer(filtered_queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='working-weekends')
    def working_weekends(self, request):
        user = request.user

        filtered_queryset = Calendar.objects.filter(day_type=Calendar.DayType.WORKING_WEEKEND)

        if not user.is_staff:
            filtered_queryset = filtered_queryset.filter(country=user.country.id)

        serializer = self.get_serializer(filtered_queryset, many=True)

        return Response(serializer.data)
