from datetime import date

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models

from apps.projects.models import ProjectCode, Task, TaskType
from apps.accounts.models import Country
from apps.clients.models import Client


User = get_user_model()

def leave_document_upload_path(instance, filename):

    return (
        f'leave_documents/'
        f'user_{instance.user_id}/'
        f'{instance.original_filename}'
    )


class CountrySettings(models.Model):
    hours_per_day = models.PositiveSmallIntegerField(default=8)
    working_days = models.JSONField(
        default=[0, 1, 2, 3, 4],
        help_text='Weekday numbers (0=Mon ... 6=Sun)'
    )
    updated_at = models.DateTimeField(auto_now=True)
    country = models.OneToOneField(
        Country,
        on_delete=models.CASCADE,
        related_name='settings'
    )

    class Meta:
        verbose_name_plural = _('Country settings')

    @classmethod
    def get_settings(cls, country_id):
        obj, created = cls.objects.get_or_create(
            country_id=country_id,
            defaults={
                'hours_per_day': 8,
                'working_days': [0, 1, 2, 3, 4],
            }
        )

        return obj

    def __str__(self):
        return f'{self.country} settings'


class LeaveDocument(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_documents'
    )
    file = models.FileField(
        upload_to=leave_document_upload_path
    )
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_filename or self.file.name


class TimeEntry(models.Model):
    date = models.DateField(null=True, blank=True)
    hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(24),
        ]
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='time_entries')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    project_code = models.ForeignKey(ProjectCode, on_delete=models.SET_NULL, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    leave_document = models.ForeignKey(
        LeaveDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries'
    )

    class Meta:
        verbose_name_plural = _('Time entries')

    def __str__(self):
        return f'{self.user.email}: {self.date}'


class Calendar(models.Model):
    class DayType(models.TextChoices):
        HOLIDAY = 'holiday', 'Holiday'
        WORKING_WEEKEND = 'working_weekend', 'Working weekend'

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

    def clean(self):
        super().clean()

        actual_year = self.year if self.year else date.today().year

        actual_date = date(
            actual_year,
            self.month,
            self.day
        )

        settings = CountrySettings.get_settings(self.country_id)
        working_days = set(settings.working_days)

        weekday = actual_date.weekday()

        if self.day_type == self.DayType.WORKING_WEEKEND:
            if weekday in working_days:
                raise ValidationError({
                    'message': 'Working weekend can only be created on non-working days.'
                })

            holiday_exists = Calendar.objects.filter(
                country=self.country,
                month=self.month,
                day=self.day,
                day_type=self.DayType.HOLIDAY,
            ).exclude(pk=self.pk).exists()

            if holiday_exists:
                raise ValidationError({
                    'message': 'Cannot create working weekend on holiday.'
                })

    def __str__(self):
        return f'{self.country} {self.month:02}-{self.day:02}'
