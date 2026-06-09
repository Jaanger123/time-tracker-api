from django.contrib.auth import get_user_model
from django.db.models import Sum, Max, Q, F

from apps.calendars.utils import get_working_days_list, filter_monitoring_by_params, calculate_missing_days, get_entries_by_user
from apps.calendars.models import CountrySettings
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

    entries_by_user = get_entries_by_user(country_id, start_date, end_date)

    working_days_list = get_working_days_list(start_date, end_date, country_id, working_days)
    required_hours = len(working_days_list) * daily_hours
    data = []

    for row in queryset:
        user_id = row['user_id']
        user_entries = entries_by_user.get(user_id, {})

        missing_days = calculate_missing_days(
            user_entries=user_entries,
            working_days_list=working_days_list,
            daily_hours=daily_hours,
        )

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