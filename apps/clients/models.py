from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models

from apps.accounts.models import Country


User = get_user_model()


class Sector(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Pie(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=150)
    group = models.CharField(max_length=150, blank=True)
    personal_number = models.CharField(max_length=150, blank=True)
    client_code = models.CharField(max_length=100, blank=True)
    bvd = models.CharField(max_length=100, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    country_of_ubo = models.ForeignKey(Country, on_delete=models.SET_NULL, related_name='ubo_projects', null=True, blank=True)
    pie = models.ForeignKey(Pie, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
