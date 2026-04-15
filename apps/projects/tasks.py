from celery import shared_task

from .services.project_code_service import (
    create_next_month_code,
    can_generate_code
)
from apps.projects.models import Project


@shared_task
def generate_monthly_project_codes():
    projects = Project.objects.filter(is_code_recurring=True)

    for project in projects:
        if not can_generate_code(project):
            continue

        create_next_month_code(project)