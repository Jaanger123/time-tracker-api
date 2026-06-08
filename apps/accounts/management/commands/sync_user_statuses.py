from datetime import date

from django.core.management.base import BaseCommand

from apps.accounts.models import (
    User,
    UserStatus,
)
from apps.accounts.services import create_user_status_history


class Command(BaseCommand):
    help = 'Populate initial user statuses'

    def handle(self, *args, **options):
        registered_status = UserStatus.objects.get(
            name=UserStatus.REGISTERED
        )

        active_status = UserStatus.objects.get(
            name=UserStatus.ACTIVE
        )

        users = User.objects.all()

        count = 0

        for user in users:
            if user.status_history.exists():
                continue

            create_user_status_history(
                user=user,
                status=registered_status,
                started_at=user.date_joined.date()
            )

            if user.is_active:
                create_user_status_history(
                    user=user,
                    status=active_status,
                    started_at=date(2026, 6, 1)
                )

            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {count} users'
            )
        )