from datetime import timedelta

from django.db.models import Q

from .models import Calendar, GlobalSettings


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