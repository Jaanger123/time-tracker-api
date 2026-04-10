from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Country, CountrySettings


@receiver(post_save, sender=Country)
def create_country_settings(sender, instance, created, **kwargs):
    if created:
        CountrySettings.objects.create(country=instance)