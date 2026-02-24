from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

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
        fields = ['id', 'name', 'position']

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
        fields = ['id', 'name', 'position']


# class GradeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Grade
#         fields = ['id', 'name']


class PositionSerializer(serializers.ModelSerializer):
    # grades = GradeSerializer(many=True, read_only=True)
    grades = GradeReadSerializer(many=True, read_only=True)

    class Meta:
        model = Grade
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

        return UserSerializer(members, many=True).data

    def get_managers(self, obj):
        managers = User.objects.filter(
            department=obj, 
            department_role__name='Manager'
        ).distinct()

        return UserSerializer(managers, many=True).data


class DepartmentDetailSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_members(self, obj):
        members = User.objects.filter(department=obj).distinct()

        return UserSerializer(members, many=True).data


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


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=6)
#     password_confirm = serializers.CharField(write_only=True, min_length=6)

#     class Meta:
#         model = User
#         fields = ('email', 'password', 'password_confirm')


#     def validate(self, attrs):
#         if attrs['password'] != attrs['password_confirm']:
#             raise serializers.ValidationError({'message': 'Passwords do not match.'})

#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()

#         return user


class ActivateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Passwords do not match')

        return data


class LogoutSerializer(serializers.Serializer):
	refresh = serializers.CharField()

	def validate(self, attrs):
		self.token = attrs.get('refresh')

		return attrs

	def save(self, **kwargs):
		try:
			RefreshToken(self.token).blacklist()
		except TokenError:
			self.fail('Incorrect token')


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    department_role = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'grade',
            'position',
            'department',
            'department_role',
            'role',
            'country',
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

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'grade',
            'position',
            'department',
            'department_role',
            'role',
            'country',
        ]

    def create(self, validated_data):
        user = User.objects.create(
            **validated_data,
            is_active=False
        )

        return user
