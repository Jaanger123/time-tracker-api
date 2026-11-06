from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.projects.models import (
    Project,
    ProjectStatusHistory,
)

class Command(BaseCommand):
    help = 'Populate initial status history for existing projects'

    def handle(self, *args, **options):
        today = timezone.localdate()

        created = 0
        skipped = 0

        for project in Project.objects.select_related(
            'status',
        ):
            if not project.status:
                print(project)
                skipped += 1
                continue

            exists = ProjectStatusHistory.objects.filter(
                project=project
            ).exists()

            if exists:
                skipped += 1
                continue

            ProjectStatusHistory.objects.create(
                project=project,
                status=project.status,
                started_at=today,
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Created: {created}, Skipped: {skipped}'
            )
        )