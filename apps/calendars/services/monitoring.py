from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db.models import Sum, Max, Q, F

from apps.calendars.utils import get_working_days_list, filter_monitoring_by_params
from apps.calendars.models import CountrySettings, TimeEntry
from apps.accounts.models import UserStatus


User = get_user_model()


def get_monitoring_data(request, country_id, start_date, end_date):
    settings = CountrySettings.get_settings(country_id)
    daily_hours = settings.hours_per_day
    working_days = set(settings.working_days)

    queryset = (
        User.objects
        .filter(
            country=country_id,
            status__name=UserStatus.ACTIVE
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
            'first_name',
            'last_name',
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

    return filter_monitoring_by_params(request, data)