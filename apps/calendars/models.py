from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models

from apps.projects.models import Project, Task, TaskType
from apps.accounts.models import Country
from apps.clients.models import Client


User = get_user_model()


class GlobalSettings(models.Model):
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8)
    working_days_of_week = models.JSONField(
        default=list,
        help_text='Weekday numbers (0=Mon ... 6=Sun)'
    )
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'hours_per_day': 8,
                'working_days_of_week': [0,1,2,3,4]
            }
        )

        return obj


class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='time_entries')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    weekends_included = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    hours = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _('Time entries')

    def __str__(self):
        return f'{self.user.email}: {self.date}'


class Calendar(models.Model):
    class DayType(models.TextChoices):
        HOLIDAY = 'holiday', 'Holiday'
        WORKING_WEEKEND = 'working_weekend', 'Working weekend'
        WORKING_DAY = 'working_day', 'Working day'

    year = models.PositiveSmallIntegerField(null=True, blank=True)
    month = models.PositiveSmallIntegerField()
    day = models.PositiveSmallIntegerField()
    holiday_name = models.CharField(max_length=255, null=True, blank=True)
    day_type = models.CharField(max_length=32, choices=DayType.choices)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['country', 'year', 'month', 'day']),
            models.Index(fields=['country', 'month', 'day']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(is_recurring=True, year__isnull=True) |
                    models.Q(is_recurring=False)
                ),
                name='recurring_has_no_year',
            ),
        ]

    def __str__(self):
        return f'{self.country} {self.month:02}-{self.day:02}'
