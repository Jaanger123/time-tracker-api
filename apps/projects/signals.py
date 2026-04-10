from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.projects.models import Project
from apps.projects.services.project_code_service import create_initial_code


@receiver(post_save, sender=Project)
def create_project_code(sender, instance, created, **kwargs):
    if created:
        create_initial_code(instance)