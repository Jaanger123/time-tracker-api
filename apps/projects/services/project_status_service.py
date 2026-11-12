from django.db import transaction
from django.utils import timezone

from apps.projects.models import ProjectStatusHistory, ProjectStatus


@transaction.atomic
def create_project_status_history(
    project,
    status,
    started_at,
):
    history = (
        ProjectStatusHistory.objects
        .filter(
            project=project,
            status=status,
        )
        .first()
    )

    if history:
        if history.started_at != started_at:
            history.started_at = started_at
            history.save(update_fields=['started_at'])
    else:
        history = ProjectStatusHistory.objects.create(
            project=project,
            status=status,
            started_at=started_at,
        )

    latest = (
        project.status_history
        .select_related('status')
        .order_by('-started_at', '-id')
        .first()
    )

    if latest:
        project.status = latest.status

        if latest.status.name == ProjectStatus.DELIVERED:
            project.closed_date = latest.started_at
        else:
            project.closed_date = None

        project.save(
            update_fields=[
                'status',
                'closed_date',
            ]
        )

    return history
