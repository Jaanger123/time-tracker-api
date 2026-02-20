from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsOwnerOrAdmin
from .serializers import *
from .models import *


class TimeEntryViewSet(ModelViewSet):
    queryset = TimeEntry.objects.all().select_related(
        'country',
        'client',
        'project',
        'task_type',
        'task'
    )
    serializer_class = TimeEntryUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_class(self):
        user = self.request.user

        if self.action in ['list', 'retrieve']:
            if user.is_staff:
                return TimeEntryAdminSerializer

            return TimeEntryUserSerializer

        return TimeEntryCreateSerializer

    def get_queryset(self):
        user = self.request.user
        
        base_queryset = TimeEntry.objects.select_related(
            'country',
            'client',
            'project',
            'task_type',
            'task',
        )

        if user.is_staff:
            return base_queryset

        return base_queryset.filter(user=user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CalendarViewSet(ModelViewSet):
    queryset = Calendar.objects.all().select_related(
        'country',
    )
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='day-types')
    def day_types(self, request):
        return Response({
            'day_types': [
                {
                    'value': value, 
                    'label': label
                }
                for value, label in Calendar.DayType.choices
            ]
        })