from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.clients.pagination import ClientPagination
from .serializers import *
from .models import *


class SectorViewSet(ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]


class PieViewSet(ModelViewSet):
    queryset = Pie.objects.all()
    serializer_class = PieSerializer
    permission_classes = [IsAuthenticated]


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all().select_related(
        'sector',
        'country',
        'pie'
    )
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.action == 'retrieve':
                return ClientDetailSerializer

            return ClientSerializer

        return ClientCreateSerializer
