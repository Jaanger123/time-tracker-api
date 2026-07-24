from datetime import timedelta

from collections import defaultdict

from apps.accounts.models import User, UserStatusHistory, UserStatus
from apps.calendars.models import TimeEntry, Calendar, CountrySettings

from .constants import *


def load_status_history(country_id):
    histories = (
        UserStatusHistory.objects
        .filter(user__country_id=country_id)
        .select_related('status')
        .order_by(
            'user_id',
            'started_at',
            'id',
        )
    )

    histories_by_user = defaultdict(list)

    for history in histories:
        histories_by_user[history.user_id].append(history)

    return histories_by_user

def get_status_for_day(histories, day):
    current_status = None

    for history in histories:
        if history.started_at > day:
            break

        current_status = history.status.name

    return current_status

def build_employment_periods(histories):
    periods = []

    current_start = None

    for history in histories:
        status = history.status.name

        if (
            status in START_STATUSES
            and current_start is None
        ):
            current_start = history.started_at

        elif (
            status in END_STATUSES
            and current_start
        ):
            periods.append(
                (
                    current_start,
                    history.started_at - timedelta(days=1),
                )
            )

            current_start = None

    if current_start:
        periods.append(
            (
                current_start,
                None,
            )
        )

    return periods

def has_overlap(
    periods,
    report_start,
    report_end,
):
    for start, end in periods:
        interval_end = end or report_end

        if (
            start <= report_end
            and interval_end >= report_start
        ):
            return True

    return False

def get_report_users(
    country_id,
    report_start,
    report_end,
):
    users = (
        User.objects
        .filter(country_id=country_id)
        .select_related(
            'department',
            'position',
            'grade',
        )
        .order_by(
            'department__name',
            'last_name',
            'first_name',
        )
    )

    histories_by_user = load_status_history(country_id)

    report_users = []

    for user in users:
        periods = build_employment_periods(
            histories_by_user[user.id]
        )

        if not has_overlap(
            periods,
            report_start,
            report_end,
        ):
            continue

        report_users.append({
            'user': user,
            'periods': periods,
            'histories': histories_by_user[user.id],
        })

    return report_users

def get_entries_by_user(
    country_id,
    start_date,
    end_date,
):
    entries = (
        TimeEntry.objects
        .filter(
            user__country_id=country_id,
            date__range=(start_date, end_date),
        )
        .select_related(
            'task',
            'task_type',
            'user',
        )
    )

    entries_by_user = defaultdict(lambda: defaultdict(list))

    for entry in entries:
        entries_by_user[entry.user_id][entry.date].append(entry)

    return entries_by_user

def summarize_entries(entries):
    '''
    Converts multiple TimeEntry objects for one day into a single summary.
    '''

    working_hours = 0
    leave_hours = 0
    leave_code = None

    for entry in entries:
        task_name = entry.task.name

        if task_name in ATTENDANCE_CODES:
            leave_code = ATTENDANCE_CODES[task_name]
            leave_hours += entry.hours
        else:
            working_hours += entry.hours

    return {
        'working_hours': working_hours,
        'leave_hours': leave_hours,
        'leave_code': leave_code,
    }

def is_employed(periods, day):
    employed = False

    for start, end in periods:
        if end is None:
            if day >= start:
                employed = True
                break
        elif start <= day <= end:
            employed = True
            break

    return employed

def build_cell(
    *,
    day,
    periods,
    calendar,
    entries,
    status,
):
    '''
    Returns the value that should be displayed inside one report cell.
    '''

    if not is_employed(periods, day):
        return {
            'value': '',
            'type': CELL_NOT_EMPLOYED,
        }

    calendar_day = calendar[day]

    summary = summarize_entries(entries)

    # maternity users
    if status == UserStatus.MATERNITY_LEAVE:
        return {
            'value': ATTENDANCE_CODES['Maternity Leave'],
            'type': CELL_MATERNITY
        }

    # leave
    if summary['leave_code']:
        if summary['working_hours'] > 0:
            return {
                    'value': f"{summary['leave_code']} ({summary['leave_hours']}, {summary['working_hours']})",
                    'type': ATTENDANCE_CODES_TYPE_MAPPING[summary['leave_code']],
                    'hours': summary['working_hours'],
                }

        return {
            'value': summary['leave_code'],
            'type': ATTENDANCE_CODES_TYPE_MAPPING[summary['leave_code']]
        }

    # holiday
    if calendar_day['is_holiday']:
        return {
            'value': CALENDAR_CODES['holiday'],
            'type': CELL_HOLIDAY,
        }

    # weekend
    if calendar_day['is_weekend']:
        return {
            'value': CALENDAR_CODES['weekend'],
            'type': CELL_WEEKEND,
        }

    # worked
    if summary['working_hours'] > 0:
        return {
            'value': str(summary['working_hours']),
            'type': CELL_WORKED,
            'hours': summary['working_hours'],
        }

    # skipped
    return {
        'value': ATTENDANCE_CODES['Skipped'],
        'type': CELL_SKIPPED,
    }

def build_calendar(
    country_id,
    start_date,
    end_date,
):
    settings = CountrySettings.get_settings(country_id)
    working_days = set(settings.working_days)

    calendar_events = (
        Calendar.objects
        .filter(
            country_id=country_id,
        )
    )

    calendar_days = {}
    calendar_map = {}

    for event in calendar_events:
        calendar_map[
            (
                event.year,
                event.month,
                event.day,
            )
        ] = event

    day = start_date

    while day <= end_date:

        weekday = day.weekday()

        is_weekend = weekday not in working_days
        is_holiday = False

        event = calendar_map.get(
            (
                day.year,
                day.month,
                day.day,
            )
        )

        recurring = calendar_map.get(
            (
                None,
                day.month,
                day.day,
            )
        )

        event = event or recurring

        if event:
            if event.day_type == Calendar.DayType.HOLIDAY:
                is_holiday = True
                is_weekend = False

            elif event.day_type == Calendar.DayType.WORKING_WEEKEND:
                is_weekend = False

        calendar_days[day] = {
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
        }

        day += timedelta(days=1)

    return calendar_days

def build_user_row(
    *,
    user,
    periods,
    histories,
    calendar,
    entries_by_day,
    report_days,
):
    row = {
        'id': user.id,
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
        'working_days': 0,
        'worked_days': 0,
        'worked_hours': 0,
        'weekends_holidays': 0,
        'paid_leaves': 0,
        'non_paid_leaves': 0,
        'business_trips': 0,
        'sick_leaves': 0,
        'day_offs': 0,
        'maternity_leave_days': 0,
        'skipped_days': 0,
    }

    for day in report_days:
        cell = build_cell(
            day=day,
            periods=periods,
            calendar=calendar,
            entries=entries_by_day.get(day, []),
            status = get_status_for_day(histories, day),
        )

        row[str(day.day)] = cell['value']

        if (
            not calendar[day]['is_weekend']
            and not calendar[day]['is_holiday']
        ):
            row['working_days'] += 1

        if cell['type'] in (
            CELL_PAID_LEAVE,
            CELL_NON_PAID_LEAVE,
            CELL_BUSINESS_TRIP,
            CELL_SICK,
            CELL_DAY_OFF
        ) and cell.get('hours'):
            row['worked_hours'] += cell['hours']

        if cell['type'] == CELL_WORKED:
            row['worked_days'] += 1
            row['worked_hours'] += cell['hours']

        elif cell['type'] == CELL_WEEKEND or cell['type'] == CELL_HOLIDAY:
            row['weekends_holidays'] += 1

        elif cell['type'] == CELL_PAID_LEAVE:
            row['paid_leaves'] += 1

        elif cell['type'] == CELL_NON_PAID_LEAVE:
            row['non_paid_leaves'] += 1

        elif cell['type'] == CELL_BUSINESS_TRIP:
            row['business_trips'] += 1

        elif cell['type'] == CELL_SICK:
            row['sick_leaves'] += 1

        elif cell['type'] == CELL_DAY_OFF:
            row['day_offs'] += 1

        elif cell['type'] == CELL_MATERNITY:
            row['maternity_leave_days'] += 1

        elif cell['type'] == CELL_SKIPPED:
            row['skipped_days'] += 1

    return row

def build_report(
    *,
    country_id,
    report_start,
    report_end,
):
    report_days = []
    current_day = report_start

    while current_day <= report_end:
        report_days.append(current_day)
        current_day += timedelta(days=1)

    calendar = build_calendar(
        country_id,
        report_start,
        report_end,
    )

    entries_by_user = get_entries_by_user(
        country_id,
        report_start,
        report_end,
    )

    report_users = get_report_users(
        country_id,
        report_start,
        report_end,
    )

    report = []

    for report_user in report_users:
        user = report_user['user']

        report.append(
            build_user_row(
                user=user,
                periods=report_user['periods'],
                histories=report_user['histories'],
                calendar=calendar,
                entries_by_day=entries_by_user.get(user.id, {}),
                report_days=report_days,
            )
        )

    return {
        'title': 'Attendance Report',
        'report_start': report_start,
        'report_end': report_end,
        'report': report,
    }
