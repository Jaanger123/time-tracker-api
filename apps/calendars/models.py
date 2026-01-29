from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models

from apps.projects.models import Project, Task, TaskType
from apps.accounts.models import Country
from apps.clients.models import Client


User = get_user_model()


class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='time_entries')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    weekends_included = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    hours = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = _('Time entries')

    def __str__(self):
        return f'{self.user.email}: {self.start_date} - {self.end_date}'
