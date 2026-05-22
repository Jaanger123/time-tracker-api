from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import models

from apps.accounts.models import Country, Department
from apps.clients.models import Client


User = get_user_model()


class ServiceType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProjectStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = _('Project statuses')

    def __str__(self):
        return self.name


class ServiceLine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=100)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    description = models.TextField(blank=True)
    entity = models.CharField(max_length=100, blank=True)
    ic = models.CharField(max_length=100, blank=True)
    project_color = models.CharField(max_length=7, default='#787878')
    is_chargeable = models.BooleanField(default=False)
    is_code_recurring = models.BooleanField(default=False)
    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    service_line = models.ForeignKey(ServiceLine, on_delete=models.SET_NULL, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=True)
    agreement_date = models.DateField()

    def get_last_project_code(self):
        project_code = ProjectCode.objects.filter(project=self.id).order_by('-created_at').first()

        return project_code.code if project_code else None

    def __str__(self):
        return self.description


class ProjectCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
