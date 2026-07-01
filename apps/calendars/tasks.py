import logging

from celery import shared_task

from calendar import monthrange

from django.contrib.auth import get_user_model
from django.utils import timezone

from .utils import get_entries_by_user, calculate_missing_days, get_working_days_list, create_licensee_time_entries
from services.email_service import send_reminder
from apps.projects.models import TaskType, Task
from apps.accounts.models import UserStatus
from .models import CountrySettings


logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_missing_time_entry_reminders():
    today = timezone.localdate()

    for settings in CountrySettings.objects.select_related('country'):
        country_id = settings.country_id

        working_days = set(settings.working_days)

        last_day = monthrange(today.year, today.month)[1]
        start_date = today.replace(day=1)
        end_date = today.replace(day=last_day)

        working_days_list = get_working_days_list(
            start_date,
            end_date,
            country_id,
            working_days,
        )

        if not working_days_list or working_days_list[-1] != today:
            continue

        entries_by_user = get_entries_by_user(
            country_id=country_id,
            start_date=start_date,
            end_date=end_date,
        )

        active_status = UserStatus.objects.get(
            name=UserStatus.ACTIVE
        )

        users = User.objects.filter(
            country=country_id,
            status=active_status,
        )

        for user in users:
            user_entries = entries_by_user.get(user.id, {})

            missing_days = calculate_missing_days(
                user_entries=user_entries,
                working_days_list=working_days_list,
                daily_hours=settings.hours_per_day,
            )

            if not missing_days:
                continue

            send_reminder.delay(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                missing_days=missing_days,
                start_date=start_date,
                end_date=end_date,
            )

@shared_task
def generate_licensee_timesheets():
    today = timezone.localdate()

    task_type = TaskType.objects.filter(name='Internal', is_active=True).first()
    task = Task.objects.filter(name='Licensee', is_active=True).first()

    if not task or not task_type:
        logger.error('Licensee auto-fill skipped: required Task or TaskType not found.')

        return

    for settings in CountrySettings.objects.select_related('country'):
        country_id = settings.country_id
        working_days = set(settings.working_days)

        last_day = monthrange(today.year, today.month)[1]

        start_date = today.replace(day=1)
        end_date = today.replace(day=last_day)

        working_days_list = get_working_days_list(
            start_date,
            end_date,
            country_id,
            working_days,
        )

        if working_days_list[-1] != today:
            continue

        users = User.objects.filter(
            country=country_id,
            status__name=UserStatus.LICENSEE,
        )

        for user in users:
            create_licensee_time_entries(
                user=user,
                working_days_list=working_days_list,
                task=task,
                task_type=task_type,
                daily_hours=settings.hours_per_day,
            )
