import logging
from celery import shared_task

from .services.project_code_service import (
    create_next_month_code,
    can_generate_code
)
from apps.projects.models import Project


logger = logging.getLogger(__name__)

@shared_task
def generate_monthly_project_codes():
    projects = Project.objects.filter(is_code_recurring=True)
    created = []
    skipped = []

    for project in projects:
        if not can_generate_code(project):
            continue

        result = create_next_month_code(project)

        if result:
            created.append(project.id)
        else:
            skipped.append(project.id)

    logger.info(f'Created {len(created)} project codes')
    logger.info(f'Skipped {len(skipped)}')