from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .services import create_user_grade_history, create_user_status_history
from apps.clients.serializers import ClientSerializer
from apps.clients.models import Client
from .models import *


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class GradeReadSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ['id', 'name', 'position', 'short_name']

    def get_position(self, obj):
        return obj.position.id if obj.position else None


class GradeCreateSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=True,
        allow_null=False,
    )

    class Meta:
        model = Grade
        fields = ['id', 'name', 'position', 'short_name']


class PositionSerializer(serializers.ModelSerializer):
    grades = GradeReadSerializer(many=True, read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'name', 'grades']


class DepartmentSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_members(self, obj):
        members = User.objects.filter(
            department=obj,
            department_role__name='Member'
        ).distinct()

        return UserReadSerializer(members, many=True).data

    def get_managers(self, obj):
        managers = User.objects.filter(
            department=obj, 
            department_role__name='Manager'
        ).distinct()

        return UserReadSerializer(managers, many=True).data


class DepartmentRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentRole
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CountryDetailSerializer(serializers.ModelSerializer):
    clients = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = '__all__'

    def get_clients(self, obj):
        clients = Client.objects.filter(project__country=obj).distinct()

        return ClientSerializer(clients, many=True).data


class ActivateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data.get('email'):
            data['email'] = data['email'].lower()

        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords do not match.')

        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, data):
        if data.get('email'):
            data['email'] = data['email'].lower()

        return super().validate(data)


class LogoutSerializer(serializers.Serializer):
	refresh = serializers.CharField()

	def validate(self, data):
		self.token = data.get('refresh')

		return data

	def save(self, **kwargs):
		try:
			RefreshToken(self.token).blacklist()
		except TokenError:
			raise serializers.ValidationError('Incorrect token')


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = '__all__'


class UserStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatusHistory
        fields = '__all__'


class UserReadSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    grade_started_at = serializers.DateField(read_only=True)
    department = serializers.SerializerMethodField()
    department_role = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    country_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_started_at = serializers.DateField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'position',
            'grade',
            'grade_started_at',
            'department',
            'department_role',
            'country',
            'country_id',
            'status',
            'status_started_at',
            'is_active',
            'date_joined',
            'date_left',
        ]

    def get_role(self, obj):
        return obj.role.name if obj.role else None

    def get_position(self, obj):
        return obj.position.name if obj.position else None

    def get_grade(self, obj):
        return obj.grade.name if obj.grade else None

    def get_department(self, obj):
        return obj.department.name if obj.department else None

    def get_department_role(self, obj):
        return obj.department_role.name if obj.department_role else None

    def get_country(self, obj):
        return obj.country.code if obj.country else None

    def get_country_id(self, obj):
        return obj.country.id if obj.country else None

    def get_status(self, obj):
        return obj.status.name if obj.status else None


class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=True,
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=True,
    )
    grade = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.all(),
        required=True,
    )
    grade_started_at = serializers.DateField(
        write_only=True,
        required=True
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=True,
    )
    department_role = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentRole.objects.all(),
        required=True,
    )
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=True,
    )
    status_started_at = serializers.DateField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'position',
            'grade',
            'grade_started_at',
            'department',
            'department_role',
            'country',
            'status_started_at',
        ]

    def validate(self, attrs):
        position = attrs.get('position')
        grade = attrs.get('grade')

        if attrs.get('email'):
            attrs['email'] = attrs['email'].lower()

        if grade and position:
            if grade.position_id != position.id:
                raise serializers.ValidationError({
                    'message':
                    'Selected grade does not belong to selected position.'
                })

        return attrs

    def create(self, validated_data):
        grade_started_at = validated_data.pop('grade_started_at')
        status_started_at = validated_data.pop('status_started_at')
        position = validated_data.pop('position')
        grade = validated_data.pop('grade')

        user = User.objects.create(
            **validated_data,
            position=position,
            grade=grade,
            is_active=False
        )

        registered_status = UserStatus.objects.get(
            name=UserStatus.REGISTERED
        )

        create_user_status_history(
            user=user,
            status=registered_status,
            started_at=status_started_at
        )

        create_user_grade_history(
            user=user,
            position=position,
            grade=grade,
            started_at=grade_started_at
        )

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    status_started_at = serializers.DateField(
        required=False
    )
    grade_started_at = serializers.DateField(
        required=False
    )

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'position',
            'grade',
            'grade_started_at',
            'department',
            'department_role',
            'country',
            'status',
            'status_started_at',
        ]

    def validate(self, attrs):
        position = attrs.get('position')
        grade = attrs.get('grade')

        if attrs.get('status') and not attrs.get('status_started_at'):
            raise serializers.ValidationError({
                'message':
                '\'status_started_at\' field is required when changing status.'
            })

        if (position and not grade) or (grade and not position):
            raise serializers.ValidationError({
                'message':
                'Please specify \'position\' and \'grade\' fields or neither.'
            })

        if attrs.get('grade') and not attrs.get('grade_started_at'):
            raise serializers.ValidationError({
                'message':
                '\'grade_started_at\' field is required when changing grade.'
            })

        if grade and position:
            if grade.position_id != position.id:
                raise serializers.ValidationError({
                    'message':
                    'Selected grade does not belong to selected position.'
                })

        return attrs

    def update(self, instance, validated_data):
        status = validated_data.pop('status', None)
        status_started_at = validated_data.pop('status_started_at', None)
        position = validated_data.pop('position', None)
        grade = validated_data.pop('grade', None)
        grade_started_at = validated_data.pop('grade_started_at', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if status is not None and status_started_at is not None:
            create_user_status_history(
                user=instance,
                status=status,
                started_at=status_started_at
            )

        if position is not None and grade is not None and grade_started_at is not None:
            create_user_grade_history(
                user=instance,
                position=position,
                grade=grade,
                started_at=grade_started_at,
            )

        return instance


class UserGradeHistorySerializer(serializers.ModelSerializer):
    position = serializers.CharField(source='position.name')
    grade = serializers.CharField(source='grade.name')

    class Meta:
        model = UserGradeHistory
        fields = [
            'id',
            'position',
            'grade',
            'started_at',
        ]


class SendRemindersSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child = serializers.EmailField()
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    subject = serializers.CharField()
    body = serializers.CharField()
