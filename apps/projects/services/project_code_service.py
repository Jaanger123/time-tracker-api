from datetime import datetime

from django.utils.timezone import now

from apps.projects.models import ProjectCode


def generate_base_code(project):
    return f'{project.country.code.upper()}_{project.client.name.upper()}_{project.department.name.upper()}_{datetime.now().year}'

def create_initial_code(project):
    base_code = generate_base_code(project)

    if project.is_code_recurring:
        code = f'{base_code}_M1'
    else:
        code = base_code

    return ProjectCode.objects.create(
        project=project,
        code=code
    )

def create_next_month_code(project):
    if already_created_this_month(project):
        return None

    last_code = project.get_last_project_code()

    if not last_code:
        return create_initial_code(project)

    # extract last M number
    if '_M' in last_code:
        current_month = int(last_code.split('_M')[-1])
    else:
        current_month = 0

    next_month = current_month + 1

    base_code = generate_base_code(project)

    new_code = f'{base_code}_M{next_month}'

    return ProjectCode.objects.create(
        project=project,
        code=new_code
    )

def can_generate_code(project):
    return (
        project.is_code_recurring and
        project.status and
        project.status.name != 'Delivered'
    )

def already_created_this_month(project):
    today = now()

    return ProjectCode.objects.filter(
        project=project,
        created_at__year=today.year,
        created_at__month=today.month
    ).exists()
