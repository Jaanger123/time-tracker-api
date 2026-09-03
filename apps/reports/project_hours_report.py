from collections import defaultdict
from datetime import timedelta

from apps.calendars.models import TimeEntry


def load_project_hours(
    *,
    country_id,
    start_date,
    end_date,
):
    grouped = {}

    entries = (
        TimeEntry.objects
        .filter(
            country_id=country_id,
            date__range=(start_date, end_date),
            project_code__isnull=False,
        )
        .select_related(
            'user',
            'user__department',
            'user__position',
            'user__grade',
            'project_code',
            'project_code__project',
            'project_code__project__client',
            'project_code__project__department',
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
        project = project_code.project

        key = (
            entry.user_id,
            project_code.id,
        )

        if key not in grouped:
            grouped[key] = {
                'user': entry.user,
                'project': project,
                'project_code': project_code,
                'hours_by_day': defaultdict(float),
            }

        grouped[key]['hours_by_day'][entry.date] += float(entry.hours)

    return grouped

def build_project_row(
    *,
    user,
    project,
    project_code,
    hours_by_day,
    report_days,
):
    total_hours = 0

    row = {
        'user_id': user.id,
        'full_name': f'{user.last_name} {user.first_name}',
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
        'project_id': project.id,
        'project_code': project_code.code,
    }

    for day in report_days:
        hours = hours_by_day.get(day, 0)

        row[str(day.day)] = hours
        total_hours += hours

    row['total_hours'] = total_hours

    return row

def build_project_hours_report(
    *,
    country_id,
    start_date,
    end_date,
):
    report_days = [
        start_date + timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    grouped = load_project_hours(
        country_id=country_id,
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
