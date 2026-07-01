from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import (
    User,
    UserGradeHistory,
)

class Command(BaseCommand):
    help = 'Populate initial grade history for existing users'

    def handle(self, *args, **options):
        today = timezone.localdate()

        created = 0
        skipped = 0

        for user in User.objects.select_related(
            'grade',
            'position',
        ):
            if not user.grade:
                skipped += 1
                continue

            exists = UserGradeHistory.objects.filter(
                user=user
            ).exists()

            if exists:
                skipped += 1
                continue

            UserGradeHistory.objects.create(
                user=user,
                position=user.position,
                grade=user.grade,
                started_at=today,
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Created: {created}, Skipped: {skipped}'
            )
        )