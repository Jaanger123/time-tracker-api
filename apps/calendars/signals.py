from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Country, CountrySettings, TimeEntry


@receiver(post_save, sender=Country)
def create_country_settings(sender, instance, created, **kwargs):
    if created:
        CountrySettings.objects.create(country=instance)

@receiver(post_delete, sender=TimeEntry)
def cleanup_leave_document(sender, instance, **kwargs):
    document = instance.leave_document

    if not document:
        return

    if not document.time_entries.exists():
        document.file.delete(save=False)
        document.delete()
