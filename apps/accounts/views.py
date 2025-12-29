from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

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


class DepartmentRoleViewSet(ModelViewSet):
    queryset = DepartmentRole.objects.all()
    serializer_class = DepartmentRoleSerializer
    permission_classes = [IsAuthenticated]


class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]


class RegisterView(APIView):
	def post(self, request):
		data = request.data
		serializer = RegisterSerializer(data=data)

		if serializer.is_valid(raise_exception=True):
			serializer.save()

			return Response({'message': 'Successfully registered'}, status.HTTP_200_OK)


class LogoutView(GenericAPIView):
	serializer_class = LogoutSerializer
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({'message': 'Successfully logged out'}, status.HTTP_200_OK)


class UserListView(ListAPIView):
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
