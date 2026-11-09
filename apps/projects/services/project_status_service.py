from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.projects.models import ProjectStatusHistory


@transaction.atomic
def create_project_status_history(
    project,
    status,
    started_at
):
    history = (
        ProjectStatusHistory.objects
        .filter(
            project=project,
            status=status,
        )
        .first()
    )

    print(started_at, history.started_at)

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

    latest = (
        project.status_history
        .select_related('status')
        .order_by('-started_at', '-id')
        .first()
    )

    if latest and project.status_id != latest.status_id:
        project.status = latest.status
        project.save(update_fields=['status'])

    return history
