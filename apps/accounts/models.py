import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models

from .managers import CustomUserManager


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades')

    def __str__(self):
        return f'{self.position if self.position else "N/A"} - {self.name}'


class DepartmentRole(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = _('Countries')

    def __str__(self):
        return f'{self.name} - {self.code}'


class UserStatus(models.Model):
    REGISTERED = 'Registered'
    ACTIVE = 'Active'
    MATERNITY_LEAVE = 'Maternity Leave'
    LICENSEE = 'Licensee'
    FIRED = 'Fired'

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = _('User statuses')
 
    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=50, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    date_left = models.DateTimeField(blank=True, null=True)
    activation_code = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True,
    )

    status = models.ForeignKey(UserStatus, on_delete=models.PROTECT, null=True, blank=True, related_name='users')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    department_role = models.ForeignKey(DepartmentRole, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def clean(self):
        if self.grade and self.position != self.grade.position:
            raise ValidationError('Grade must belong to selected position.')

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()

        super().save(*args, **kwargs)


class UserStatusHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    status = models.ForeignKey(
        UserStatus,
        on_delete=models.PROTECT
    )

    started_at = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name_plural = _('User status history')
        ordering = ['started_at']

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'status',
                    'started_at'
                ],
                name='unique_user_status_date'
            )
        ]

    def __str__(self):
        return f'{self.user.email}: {self.status.name}. On: {self.started_at}'
