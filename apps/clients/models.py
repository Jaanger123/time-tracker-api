from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=150)
    group = models.CharField(max_length=150)
    personal_number = models.CharField(max_length=150)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
