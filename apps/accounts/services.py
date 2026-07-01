from django.db import transaction

from .models import UserStatusHistory, UserGradeHistory


@transaction.atomic
def create_user_status_history(
    user,
    status,
    started_at
):
    latest = (
        UserStatusHistory.objects
        .filter(user=user)
        .order_by('-started_at', '-id')
        .first()
    )

    if (
        latest
        and latest.status_id == status.id
        and latest.started_at == started_at
    ):
        return latest

    history = UserStatusHistory.objects.create(
        user=user,
        status=status,
        started_at=started_at
    )

    user.status = status
    user.save(update_fields=['status'])

    return history

@transaction.atomic
def create_user_grade_history(
    user,
    position,
    grade,
    started_at,
):
    latest = (
        UserGradeHistory.objects
        .filter(user=user)
        .order_by('-started_at', '-id')
        .first()
    )

    if (
        latest
        and latest.position_id == position.id
        and latest.grade_id == grade.id
        and latest.started_at == started_at
    ):
        return latest

    history = UserGradeHistory.objects.create(
        user=user,
        position=position,
        grade=grade,
        started_at=started_at,
    )

    user.position = position
    user.grade = grade

    user.save(update_fields=['position', 'grade'])

    return history
