from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

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


class LeaveDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveDocument
        fields = '__all__'


class TimeEntryReadSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    project_color = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    leave_document = serializers.SerializerMethodField()

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

    def get_leave_document(self, obj):
        if not obj.leave_document:
            return None

        return {
            'id': obj.leave_document.id,
            'name': Path(obj.leave_document.file.name).name,
            'url': obj.leave_document.file.url,
        }


class TimeEntryAdminReadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    country = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    project_color = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    leave_document = serializers.SerializerMethodField()

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

    def get_leave_document(self, obj):
        if not obj.leave_document:
            return None

        return {
            'id': obj.leave_document.id,
            'name': Path(obj.leave_document.file.name).name,
            'url': obj.leave_document.file.url,
        }


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    weekends_included = serializers.BooleanField(write_only=True, default=False)
    holidays_included = serializers.BooleanField(write_only=True, default=False)
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
    leave_document = serializers.FileField(
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = TimeEntry
        exclude = ['user']

    def validate(self, attrs):
        request = self.context.get('request')
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if request.method in ['PUT', 'PATCH']:
            return attrs

        if 'date' in attrs:
            attrs.pop('date')

        if not start_date or not end_date:
            raise serializers.ValidationError(
                {'message': 'Provide \'start_date\' and \'end_date\'.'}
            )

        if start_date > end_date:
            raise serializers.ValidationError(
                {'message': '\'start_date\' cannot be greater than \'end_date\'.'}
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        weekends_included = validated_data.pop('weekends_included', False)
        holidays_included = validated_data.pop('holidays_included', False)
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)
        single_date = request.query_params.get('single_date', 'false')
        leave_document = validated_data.pop('leave_document', None)

        leave_document_obj = None

        if leave_document:
            leave_document_obj = LeaveDocument.objects.create(
                user=self.context['request'].user,
                file=leave_document
            )

        if start_date == end_date and single_date == 'true':
            return TimeEntry.objects.create(
                date=start_date,
                leave_document=leave_document_obj,
                **validated_data
            )

        years = list(range(start_date.year, end_date.year + 1))

        calendar_events = Calendar.objects.filter(
            country=request.user.country
        ).filter(
            Q(is_recurring=True) |
            Q(is_recurring=False, year__in=years)
        )

        holidays = set()
        working_weekends = set()

        for event in calendar_events:
            if event.is_recurring:
                day = (event.month, event.day)
            else:
                day = (event.year, event.month, event.day)

            if event.day_type == Calendar.DayType.HOLIDAY:
                holidays.add(day)

            elif event.day_type == Calendar.DayType.WORKING_WEEKEND:
                working_weekends.add(day)

        entries = []
        current_date = start_date

        while current_date <= end_date:
            key_full = (current_date.year, current_date.month, current_date.day)
            key_recurring = (current_date.month, current_date.day)

            is_holiday = key_full in holidays or key_recurring in holidays
            is_working_weekend = key_full in working_weekends or key_recurring in working_weekends

            if not weekends_included and current_date.weekday() >= 5 and not is_working_weekend:
                current_date += timedelta(days=1)
                continue

            if not holidays_included and is_holiday:
                current_date += timedelta(days=1)
                continue

            entries.append(
                TimeEntry(
                    date=current_date,
                    leave_document=leave_document_obj,
                    **validated_data
                )
            )
            current_date += timedelta(days=1)

        if not entries:
            raise serializers.ValidationError(
                'There are no working days in the selected range.'
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
        instance = Calendar(**validated_data)

        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()

        return instance

    def update(self, instance, validated_data):
        validated_data.pop('input_date')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()

        return instance
