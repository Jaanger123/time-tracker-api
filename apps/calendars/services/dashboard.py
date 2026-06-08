from calendar import monthrange

from datetime import date

from django.db.models import Sum

from apps.calendars.models import CountrySettings, TimeEntry
from apps.calendars.utils import get_working_days_list


def get_dashboard_data(user, year, month):
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])

    settings = CountrySettings.get_settings(user.country_id)

    daily_hours = settings.hours_per_day
    working_days = set(settings.working_days)

    queryset = TimeEntry.objects.filter(
        user=user,
        date__range=(start_date, end_date)
    )

    total_hours = (
        queryset.aggregate(
            total=Sum('hours')
        )['total'] or 0
    )

    total_records = queryset.count()

    working_days_list = get_working_days_list(
        start_date,
        end_date,
        user.country_id,
        working_days
    )

    total_working_days = len(working_days_list)

    expected_hours = total_working_days * daily_hours

    worked_days = (
        queryset.values_list('date', flat=True)
        .distinct()
        .count()
    )

    completion_rate = 0

    if expected_hours > 0:
        completion_rate = round(
            (total_hours / expected_hours) * 100,
            2
        )

    return {
        'total_hours': total_hours,
        'expected_hours': expected_hours,
        'completion_rate': completion_rate,
        'worked_days': worked_days,
        'total_working_days': total_working_days,
        'total_records': total_records,
    }