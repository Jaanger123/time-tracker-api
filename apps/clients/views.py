from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from .serializers import ClientSerializer
from .models import Client


class ClientListView(ListAPIView):
    queryset = Client.objects.all().select_related(
        'manager', 
        'sector'
    )
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]