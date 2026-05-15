from django.db.models import F

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from apps.clients.pagination import ClientPagination
from .filters import ClientFilter
from .serializers import *
from .models import *


class SectorViewSet(ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class PieViewSet(ModelViewSet):
    queryset = Pie.objects.all()
    serializer_class = PieSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all().select_related(
        'sector',
        'country',
        'pie'
    )
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ClientFilter
    ordering_fields = ['name', 'group', 'personal_number', 'sector_name']

    def get_queryset(self):
        return Client.objects.annotate(
            sector_name=F('sector__name'),
        )

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.action == 'retrieve':
                return ClientDetailSerializer

            return ClientSerializer

        return ClientCreateSerializer
