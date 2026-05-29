from datetime import datetime, date
from sqlite3 import IntegrityError

from apps.projects.models import ProjectCode


def generate_base_code(project, year):
    # country_department_client(-project-entity)_year_project-type
    code_structure = [
        project.country.code.upper(),
        project.department.code.upper(),
        project.client.client_code.upper() + (('-' + project.entity.upper()) if project.entity != '' else ''),
        year,
        project.service_type.name.upper()
    ]

    return '_'.join(code_structure)

def get_months(start_date, end_date):
    current = start_date.replace(day=1)
    months = []

    while current <= end_date:
        months.append(current)
        month = current.month % 12 + 1
        year = current.year + (current.month // 12)
        current = date(year, month, 1)

    return months

def create_initial_code(project):
    try:
        if project.is_code_recurring:
            today = datetime.now().date()
            months = get_months(
                start_date=project.agreement_date,
                end_date=today
            )
            project_codes = []

            for month in months:
                code = generate_base_code(
                    project=project, 
                    year=str(month.year)
                ) + f'_M{month.month:02d}'
                project_codes.append(ProjectCode(project=project, code=code))

            return ProjectCode.objects.bulk_create(project_codes)

        else:
            base_code = generate_base_code(
                project=project, 
                year=str(project.agreement_date.year)
            )
            queryset = ProjectCode.objects.filter(project=project)
            last_code_number = 0

            for obj in queryset:
                code_number = int(obj.code.split('_')[-1])
                last_code_number = max(last_code_number, code_number)

            code = base_code + f'_{last_code_number + 1:02d}'

            return ProjectCode.objects.create(
                project=project,
                code=code
            )
    except Exception:
        return False

def create_next_month_code(project):
    if already_created_this_month(project):
        return False

    last_code = project.get_last_project_code()
    today = datetime.now().date()

    if not last_code:
        return create_initial_code(project)

    base_code = generate_base_code(
        project=project, 
        year=str(today.year)
    )
    new_code = f'{base_code}_M{today.month:02d}'

    try:
        ProjectCode.objects.create(
            project=project,
            code=new_code
        )

        return True
    except IntegrityError:
        return False

def can_generate_code(project):
    return (
        project.is_code_recurring and
        project.status and
        project.status.name == 'In progress'
    )

def already_created_this_month(project):
    today = datetime.now()

    return ProjectCode.objects.filter(
        project=project,
        created_at__year=today.year,
        created_at__month=today.month
    ).exists()
