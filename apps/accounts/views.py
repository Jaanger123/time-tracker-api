from datetime import date

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from django.db.models import F, OuterRef, Subquery

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
from utils import generate_excel
from .filters import UserFilter
from .serializers import *
from .models import *


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

        active_status = UserStatus.objects.get(
            name=UserStatus.ACTIVE
        )

        create_user_status_history(
            user=user,
            status=active_status,
            started_at=date.today()
        )

        return Response({'message': 'Account activated'})


class LogoutView(GenericAPIView):
	serializer_class = LogoutSerializer
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({'message': 'Successfully logged out'}, status.HTTP_200_OK)


class UserStatusViewSet(ModelViewSet):
    queryset = UserStatus.objects.all()
    serializer_class = UserStatusSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None


class UserStatusHistoryViewSet(ModelViewSet):
    queryset = UserStatusHistory.objects.all()
    serializer_class = UserStatusHistorySerializer
    permission_classes = [IsAdminRole]
    pagination_class = None


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().select_related(
        'role', 
        'position', 
        'grade', 
        'department', 
        'department_role', 
        'country',
        'status',
    ).order_by('id')
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
        'status_name',
        'date_joined',
    ]

    def _export_excel(self, queryset):
        columns = [
            'first_name',
            'last_name',
            'email',
            'status_name',
            'phone_number',
            'role_name',
            'position_name',
            'grade_name',
            'department_name',
            'department_role_name',
            'country_code',
            'date_joined',
            'date_left',
        ]

        headers = [
            'First Name',
            'Last Name',
            'Email',
            'Status',
            'Phone Number',
            'Role',
            'Position',
            'Grade',
            'Department',
            'Department Role',
            'Country',
            'Date Joined',
            'Date Left',
        ]

        return generate_excel(queryset, 'Users', columns, headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        export_type = request.query_params.get('export')

        if export_type == 'excel':
            return self._export_excel(queryset)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()

        latest_status_date = (
            UserStatusHistory.objects
            .filter(user=OuterRef('pk'))
            .order_by('-started_at', '-id')
            .values('started_at')[:1]
        )

        return queryset.annotate(
            position_name=F('position__name'),
            department_name=F('department__name'),
            department_role_name=F('department_role__name'),
            grade_name=F('grade__name'),
            country_code=F('country__code'),
            role_name=F('role__name'),
            status_name=F('status__name'),
            status_started_at=Subquery(latest_status_date),
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer

        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer

        return UserReadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'me', 'managers']:
            return [IsAuthenticated()]

        return [IsAdminRole()]

    def perform_create(self, serializer):
        user = serializer.save()
        send_activation_email(user)

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
