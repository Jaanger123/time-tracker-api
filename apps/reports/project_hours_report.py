from collections import defaultdict
from datetime import timedelta

from django.db.models import Q

from apps.calendars.models import TimeEntry
from apps.projects.models import TaskType


def load_project_hours(
    *,
    start_date,
    end_date,
):
    grouped = {}

    entries = (
        TimeEntry.objects
        .filter(
            Q(project_code__isnull=False)
            | Q(task_type__name=TaskType.INTERNAL),
            date__range=(start_date, end_date),
        )
        .select_related(
            'user',
            'user__country',
            'user__department',
            'user__position',
            'user__grade',
            'task',
            'project_code',
            'project_code__project',
            'project_code__project__client',
            'project_code__project__department',
            'project_code__project__country',
        )
        .order_by(
            'user__email',
            'project_code__code',
            'date',
            'id',
        )
    )

    for entry in entries:
        project_code = entry.project_code
        project = project_code.project if project_code else None
        task = entry.task

        if project_code:
            key = (
                entry.user_id,
                'project',
                project_code.id,
            )
        else:
            key = (
                entry.user_id,
                'internal',
                entry.task_id,
            )

        if key not in grouped:
            grouped[key] = {
                'user': entry.user,
                'project': project,
                'project_code': project_code,
                'task': task if not project_code else None,
                'hours_by_day': defaultdict(float),
            }

        grouped[key]['hours_by_day'][entry.date] += float(entry.hours)

    return grouped

def build_project_row(
    *,
    user,
    project,
    project_code,
    task,
    hours_by_day,
    report_days,
):
    total_hours = 0

    row = {
        'user_id': user.id,
        'full_name': f'{user.last_name} {user.first_name}',
        'user_country_code': (
            user.country.code
            if user.country
            else ''
        ),
        'department': (
            user.department.name
            if user.department
            else ''
        ),
        'position': (
            user.position.name
            if user.position
            else ''
        ),
        'grade': (
            user.grade.name
            if user.grade
            else ''
        ),
        'project_id': (
            project.id
            if project
            else None
        ),
        'project_country_code': (
            project.country.code
            if project and project.country
            else ''
        ),
        'project_code': (
            project_code.code
            if project_code
            else ''
        ),
        'task_name': (
            task.name
            if task
            else ''
        ),
    }

    for day in report_days:
        hours = hours_by_day.get(day, 0)

        row[str(day.day)] = hours
        total_hours += hours

    row['total_hours'] = total_hours

    return row

def build_project_hours_report(
    *,
    start_date,
    end_date,
):
    report_days = [
        start_date + timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    grouped = load_project_hours(
        start_date=start_date,
        end_date=end_date,
    )

    rows = []

    for data in grouped.values():
        rows.append(
            build_project_row(
                user=data['user'],
                project=data['project'],
                project_code=data['project_code'],
                task=data['task'],
                hours_by_day=data['hours_by_day'],
                report_days=report_days,
            )
        )

    rows.sort(
        key=lambda row: (
            row['full_name'],
            row['project_code'],
        )
    )

    return rows
