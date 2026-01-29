from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import *
from .models import *


User = get_user_model()


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    # @action(detail=True, methods=['get'])
    # def members(self, request):
    #     members = User.objects.filter(task_type__name='Internal')
    #     serializer = TaskSerializer(tasks, many=True)

    #     return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailSerializer

        return DepartmentSerializer


class DepartmentRoleViewSet(ModelViewSet):
    queryset = DepartmentRole.objects.all()
    serializer_class = DepartmentRoleSerializer
    permission_classes = [IsAuthenticated]


class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CountryDetailSerializer

        return CountrySerializer


# class RegisterView(APIView):
# 	def post(self, request):
# 		data = request.data
# 		serializer = RegisterSerializer(data=data)

# 		if serializer.is_valid(raise_exception=True):
# 			serializer.save()

# 			return Response({'message': 'Successfully registered'}, status.HTTP_200_OK)


class ActivateUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ActivateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            email=serializer.validated_data['email'],
            activation_code=serializer.validated_data['activation_code'],
            is_active=False,
        )

        user.set_password(serializer.validated_data['password'])
        user.is_active = True
        user.activation_code = None
        user.save()

        return Response({'detail': 'Account activated'})


class LogoutView(GenericAPIView):
	serializer_class = LogoutSerializer
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({'message': 'Successfully logged out'}, status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().select_related(
        'role', 
        'position', 
        'grade', 
        'department', 
        'department_role', 
        'country'
    )
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserSerializer

        return UserCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]

        return [IsAdminUser()]