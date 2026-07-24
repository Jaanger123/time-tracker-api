from apps.accounts.models import UserStatus


CELL_WORKED = 'worked'
CELL_WEEKEND = 'weekend'
CELL_HOLIDAY = 'holiday'
CELL_PAID_LEAVE = 'paid_leave'
CELL_NON_PAID_LEAVE = 'non_paid_leave'
CELL_BUSINESS_TRIP = 'business_trip'
CELL_SICK = 'sick_leave'
CELL_DAY_OFF = 'day_off'
CELL_MATERNITY = 'maternity'
CELL_SKIPPED = 'skipped'
CELL_NOT_EMPLOYED = 'not_employed'

ATTENDANCE_CODES = {
    'Business trip': 'К',
    'Paid leave': 'О',
    'Non-paid leave': 'ОБС',
    'Sick leave': 'Б',
    'Maternity Leave': 'Р',
    'Day off': 'ДО',
    'Skipped': 'П',
}

ATTENDANCE_CODES_TYPE_MAPPING = {
    'К': CELL_BUSINESS_TRIP,
    'О': CELL_PAID_LEAVE,
    'ОБС': CELL_NON_PAID_LEAVE,
    'Б': CELL_SICK,
    'Р': CELL_MATERNITY,
    'ДО': CELL_DAY_OFF,
    'П': CELL_SKIPPED,

}

CALENDAR_CODES = {
    'weekend': 'Е',
    'holiday': 'ПР',
}

START_STATUSES = {
    UserStatus.ACTIVE,
    UserStatus.MATERNITY_LEAVE,
    UserStatus.LICENSEE,
    UserStatus.REGISTERED,
}

END_STATUSES = {
    UserStatus.FIRED,
}