from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .serializers import *
from .models import Client


class SectorViewSet(ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all().select_related(
        'sector',
    )
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.action == 'retrieve':
                return ClientDetailSerializer

            return ClientSerializer

        return ClientCreateSerializer
