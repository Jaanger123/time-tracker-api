from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from django.db.models import F

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainPairView

from django_filters.rest_framework import DjangoFilterBackend

from services.email_service import send_activation_email, send_reminder, send_message
from apps.accounts.pagination import UserPagination
from .permissions import IsAdminRole
from .serializers import *
from .models import *
from .filters import UserFilter


User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all().select_related(
        'position'
    )
    serializer_class = GradeReadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GradeReadSerializer

        return GradeCreateSerializer


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    # @action(detail=True, methods=['get'])
    # def members(self, request):
    #     members = User.objects.filter(task_type__name='Internal')
    #     serializer = TaskSerializer(tasks, many=True)

    #     return Response(serializer.data)

    def get_serializer_class(self):
        # if self.action == 'retrieve':
        #     return DepartmentDetailSerializer

        return DepartmentSerializer


class DepartmentRoleViewSet(ModelViewSet):
    queryset = DepartmentRole.objects.all()
    serializer_class = DepartmentRoleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CountryDetailSerializer

        return CountrySerializer


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
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = UserFilter
    ordering_fields = [
        'first_name', 
        'last_name', 
        'email', 
        'position_name', 
        'department_name', 
        'department_role_name', 
        'grade_name',
        'country_code',
        'role_name',
        'date_joined',
        'is_active'
    ]

    @action(detail=False, methods=['get'])
    def managers(self, request):
        managers = User.objects.filter(department_role__name='Manager')
        serializer = UserReadSerializer(managers, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserReadSerializer(request.user)

        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='send-reminders')
    def send_reminders(self, request):
        serializer = SendRemindersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        not_sent = []

        for email in serializer.validated_data['emails']:
            is_sent = send_reminder(
                email, 
                serializer.validated_data['start_date'], 
                serializer.validated_data['end_date']
            )

            if not is_sent:
                not_sent.append(email)

        message = 'Reminders sent successfully'

        if not_sent:
            message += f', except: {not_sent}'

        return Response({'message': message}, status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='send-message')
    def send_message(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_message(
            serializer.validated_data['email'], 
            serializer.validated_data['subject'], 
            serializer.validated_data['body']
        )

        return Response({'message': 'Email sent successfully'}, status.HTTP_200_OK)

    def get_queryset(self):
        return User.objects.annotate(
            position_name=F('position__name'),
            department_name=F('department__name'),
            department_role_name=F('department_role__name'),
            grade_name=F('grade__name'),
            country_code=F('country__code'),
            role_name=F('role__name'),
        )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserReadSerializer

        return UserCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'me', 'managers']:
            return [IsAuthenticated()]

        return [IsAdminRole()]

    def perform_create(self, serializer):
        user = serializer.save()
        send_activation_email(user)
