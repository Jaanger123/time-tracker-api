from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Country, CountrySettings, TimeEntry, LeaveDocument


@receiver(post_save, sender=Country)
def create_country_settings(sender, instance, created, **kwargs):
    if created:
        CountrySettings.objects.create(country=instance)

@receiver(post_delete, sender=TimeEntry)
def cleanup_leave_document(sender, instance, **kwargs):
    document_id = instance.leave_document_id

    if not document_id:
        return

    if TimeEntry.objects.filter(
        leave_document_id=document_id
    ).exists():
        return

    document = LeaveDocument.objects.filter(
        id=document_id
    ).first()

    if not document:
        return

    document.file.delete(save=False)
    document.delete()
