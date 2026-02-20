from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import *


User = get_user_model()


class TimeEntryUserSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    project_color = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        exclude = ['user']

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_client(self, obj):
        return obj.client.name if obj.client else None

    def get_project(self, obj):
        return obj.project.name if obj.project else None

    def get_project_color(self, obj):
        return obj.project.project_color if obj.project else None

    def get_project_code(self, obj):
        return obj.project.code if obj.project else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None

    def get_task(self, obj):
        return obj.task.name if obj.task else None


class TimeEntryAdminSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    project_color = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = '__all__'

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_client(self, obj):
        return obj.client.name if obj.client else None

    def get_project(self, obj):
        return obj.project.name if obj.project else None

    def get_project_color(self, obj):
        return obj.project.project_color if obj.project else None

    def get_project_code(self, obj):
        return obj.project.code if obj.project else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None

    def get_task(self, obj):
        return obj.task.name if obj.task else None


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True,
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=False,
        allow_null=True,
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        required=False,
        allow_null=True,
    )
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=False,
        allow_null=True,
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = TimeEntry
        exclude = ['user']


class CalendarSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    input_date = serializers.DateField(write_only=True)

    class Meta:
        model = Calendar
        fields = [
            'id',
            'date',
            'input_date',
            'holiday_name',
            'day_type',
            'description',
            'is_recurring',
            'country',
        ]

    def get_date(self, obj):
        if obj.year:
            return f'{obj.year}-{obj.month:02}-{obj.day:02}'

        return f'{obj.month:02}-{obj.day:02}'

    def validate(self, data):
        if self.instance is None and 'input_date' not in data:
            raise serializers.ValidationError(
                {'input_date': 'This field is required.'}
            )

        date = data.get('input_date')
        is_recurring = data.get('is_recurring')
        day_type = data.get('day_type')
        holiday_name = data.get('holiday_name')

        if self.instance is None and \
        day_type == Calendar.DayType.HOLIDAY and \
        not holiday_name:
            raise ValidationError(
                {'holiday_name': 'Holiday name is required for holidays.'}
            )

        if self.instance is None and \
        day_type != Calendar.DayType.HOLIDAY and \
        holiday_name:
            raise ValidationError(
                {'holiday_name': 'Holiday name is allowed only for holidays.'}
            )

        if self.instance and not date and is_recurring == False:
            raise ValidationError(
                {'input_date': 'Recurring event can not exist without a year.'}
            )

        if self.instance and day_type != Calendar.DayType.HOLIDAY:
            data['holiday_name'] = None

        if date:
            data['month'] = date.month
            data['day'] = date.day
            data['year'] = None if is_recurring else date.year

        elif is_recurring == True and self.instance:
            data['year'] = None

        return data

    def create(self, validated_data):
        validated_data.pop('input_date')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('input_date', None)

        return super().update(instance, validated_data)
