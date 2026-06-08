from django.db import transaction

from .models import UserStatusHistory


@transaction.atomic
def create_user_status_history(
    user,
    status,
    started_at
):
    history = UserStatusHistory.objects.create(
        user=user,
        status=status,
        started_at=started_at
    )

    latest = (
        user.status_history
        .order_by('-started_at', '-id')
        .first()
    )

    user.status = latest.status
    user.save(update_fields=['status'])

    return history