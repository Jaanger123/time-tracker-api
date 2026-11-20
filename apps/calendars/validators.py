from datetime import timedelta

from rest_framework.exceptions import ValidationError

from django.utils import timezone


def validate_time_entry_period(start_date, end_date=None):
    today = timezone.localdate()

    current_month_start = today.replace(day=1)

    if today.day <= 10:
        allowed_from = (
            current_month_start - timedelta(days=1)
        ).replace(day=1)
    else:
        allowed_from = current_month_start

    next_month_start = (
        current_month_start + timedelta(days=32)
    ).replace(day=1)

    end_date = end_date or start_date

    if start_date < allowed_from or end_date < allowed_from:
        raise ValidationError({
            'message': 'You cannot craete or modify entries from previous months.'
        })

    if start_date >= next_month_start or end_date >= next_month_start:
        raise ValidationError({
            'message': 'You cannot create or modify entries for future months.'
        })