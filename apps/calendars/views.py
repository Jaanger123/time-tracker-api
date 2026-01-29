from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

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
