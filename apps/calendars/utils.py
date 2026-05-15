from datetime import timedelta, datetime

from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.db.models import Q

from apps.accounts.models import Country
from .models import Calendar


class CompletionStatus:
    MISSING = 'missing'
    PARTIAL = 'partial'
    COMPLETED = 'completed'


def get_working_days_list(start_date, end_date, country, working_weekdays={0, 1, 2, 3, 4}):
    calendar_events = Calendar.objects.filter(
        country=country
    ).filter(
        Q(is_recurring=True) |
        Q(year__gte=start_date.year, year__lte=end_date.year)
    )

    holiday_set = set()
    working_weekend_set = set()

    for event in calendar_events:
        if event.is_recurring:
            key = (event.month, event.day)
        else:
            key = (event.year, event.month, event.day)

        if event.day_type == Calendar.DayType.HOLIDAY:
            holiday_set.add(key)
        elif event.day_type == Calendar.DayType.WORKING_WEEKEND:
            working_weekend_set.add(key)

    total_days = []
    current = start_date

    while current <= end_date:
        weekday = current.weekday()
        is_working_day = weekday in working_weekdays
        recurring_key = (current.month, current.day)
        specific_key = (current.year, current.month, current.day)

        if recurring_key in holiday_set or specific_key in holiday_set:
            is_working_day = False

        if recurring_key in working_weekend_set or specific_key in working_weekend_set:
            is_working_day = True

        if is_working_day:
            total_days.append(current)

        current += timedelta(days=1)

    return total_days

def get_country(request):
    country_id = request.query_params.get('country')

    if not country_id:
        return None, Response(
            {'error': '\'country\' query param is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        country = Country.objects.get(id=country_id)

        return country, None

    except Country.DoesNotExist:
        return None, Response(
            {'error': 'Country not found'},
            status=status.HTTP_404_NOT_FOUND
        )

def filter_report_by_params(request, queryset):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    date = request.query_params.get('date')
    user_email = request.query_params.get('user_email')
    client_name = request.query_params.get('client_name')
    code = request.query_params.get('code')
    user_department = request.query_params.get('user_department')
    project_department = request.query_params.get('project_department')
    country_code = request.query_params.get('country_code')
    position = request.query_params.get('position')
    detailed_grade = request.query_params.get('detailed_grade')
    project_service_line = request.query_params.get('project_service_line')
    description = request.query_params.get('description')
    task_name = request.query_params.get('task_name')

    if start_date:
        queryset = queryset.filter(date__gte=start_date)

    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    if date:
        queryset = queryset.filter(date=date)

    if date:
        queryset = queryset.filter(date=date)

    if user_email:
        queryset = queryset.filter(user__email__icontains=user_email)

    if client_name:
        queryset = queryset.filter(client__name__icontains=client_name)

    if code:
        queryset = queryset.filter(project_code__code__icontains=code)

    if user_department:
        queryset = queryset.filter(user__department__name__icontains=user_department)

    if project_department:
        queryset = queryset.filter(project_code__project__department__name__icontains=project_department)

    if country_code:
        queryset = queryset.filter(country__code__icontains=country_code)

    if position:
        queryset = queryset.filter(user__position__name__icontains=position)

    if detailed_grade:
        queryset = queryset.filter(user__grade__name__icontains=detailed_grade)

    if project_service_line:
        queryset = queryset.filter(project_code__project__service_line__name__icontains=project_service_line)

    if description:
        queryset = queryset.filter(description__icontains=description)

    if task_name:
        queryset = queryset.filter(task__name__icontains=task_name)

    return queryset

def parse_date(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return timezone.make_aware(dt)
    except:
        return None

def filter_monitoring_by_params(request, data):
    user_email = request.query_params.get('user_email', '').lower()
    first_name = request.query_params.get('first_name', '').lower()
    last_name = request.query_params.get('last_name', '').lower()
    updated_after = request.query_params.get('updated_after')
    updated_before = request.query_params.get('updated_before')
    completion = request.query_params.get('completion', '').lower()

    updated_after = parse_date(updated_after)
    updated_before = parse_date(updated_before)

    new_data = []

    for obj in data:
        if not user_email in obj['user_email']:
            continue

        if not first_name in (obj['first_name'] or '').lower():
            continue

        if not last_name in (obj['last_name'] or '').lower():
            continue

        last_updated = obj.get('last_updated')

        if updated_after and (not last_updated or last_updated < updated_after):
            continue

        if updated_before and (not last_updated or last_updated > updated_before):
            continue

        if completion == CompletionStatus.MISSING and obj['completion'] != 0:
            continue

        if completion == CompletionStatus.PARTIAL and (obj['completion'] == 0 or obj['completion'] >= 100):
            continue

        if completion == CompletionStatus.COMPLETED and obj['completion'] < 100:
            continue

        new_data.append(obj)

    return new_data
