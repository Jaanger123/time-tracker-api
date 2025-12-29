from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from .models import *


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']


class PositionSerializer(serializers.ModelSerializer):
    grades = GradeSerializer(many=True, read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'name', 'grades']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DepartmentRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentRole
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm')


    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'message': 'Passwords do not match.'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


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
    role = serializers.ReadOnlyField(source='role.name')
    position = serializers.ReadOnlyField(source='position.name')
    grade = serializers.ReadOnlyField(source='grade.name')
    department = serializers.ReadOnlyField(source='department.name')
    department_role = serializers.ReadOnlyField(source='department_role.name')
    country = serializers.ReadOnlyField(source='country.code')

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'position',
            'grade',
            'department',
            'department_role',
            'country',
            'date_joined',
            'date_left',
            'is_active',
        ]
