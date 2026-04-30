from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

from .models import *


User = get_user_model()


class CountrySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountrySettings
        fields = [
            'country',
            'hours_per_day',
            'working_days',
            'updated_at',
        ]
        read_only_fields = ['updated_at']

    def validate_working_days(self, value):
        if not all(0 <= day <= 6 for day in value):
            raise serializers.ValidationError('Days must be between 0 and 6')

        return value


class TimeEntryReadSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
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

    def get_project_color(self, obj):
        return obj.project_code.project.project_color if obj.project_code and obj.project_code.project else None

    def get_project_code(self, obj):
        return obj.project_code.code if obj.project_code else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None

    def get_task(self, obj):
        return obj.task.name if obj.task else None


class TimeEntryAdminReadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
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

    def get_project_color(self, obj):
        return obj.project_code.project.project_color if obj.project_code and obj.project_code.project else None

    def get_project_code(self, obj):
        return obj.project_code.code if obj.project_code else None

    def get_task_type(self, obj):
        return obj.task_type.name if obj.task_type else None

    def get_task(self, obj):
        return obj.task.name if obj.task else None


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=False, write_only=True)
    end_date = serializers.DateField(required=False, write_only=True)

    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=False,
        allow_null=True
        
    )
    project_code = serializers.PrimaryKeyRelatedField(
        queryset=ProjectCode.objects.all(),
        required=False,
        allow_null=True
        
    )
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=True
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=True
    )

    class Meta:
        model = TimeEntry
        exclude = ['user']

    def validate(self, attrs):
        request = self.context.get('request')
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        date = attrs.get('date')

        if request.method in ['PUT', 'PATCH']:
            return attrs

        if not date and (not start_date or not end_date):
            raise serializers.ValidationError(
                'Provide \'{date}\' or \'start_date\' and \'end_date\'.'
            )

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    '\'start_date\' cannot be greater than \'end_date\'.'
                )

        return attrs

    def create(self, validated_data):
        weekends_included = validated_data.get('weekends_included', False)
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)

        if not start_date or not end_date:
            return TimeEntry.objects.create(
                **validated_data
            )

        entries = []
        current_date = start_date

        while current_date <= end_date:
            if not weekends_included and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            entries.append(
                TimeEntry(
                    date=current_date,
                    **validated_data
                )
            )
            current_date += timedelta(days=1)

        if not entries:
            raise serializers.ValidationError(
                'Selected range contains only weekends and weekends are not included.'
            )

        with transaction.atomic():
            TimeEntry.objects.bulk_create(entries)

        return entries[-1]


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
            raise serializers.ValidationError(
                {'holiday_name': 'Holiday name is required for holidays.'}
            )

        if self.instance is None and \
        day_type != Calendar.DayType.HOLIDAY and \
        holiday_name:
            raise serializers.ValidationError(
                {'holiday_name': 'Holiday name is allowed only for holidays.'}
            )

        if self.instance and not date and is_recurring == False:
            raise serializers.ValidationError(
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
