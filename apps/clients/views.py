from django.db.models import F

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

from apps.clients.pagination import ClientPagination
from .filters import ClientFilter
from utils import generate_excel
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
        'country_of_ubo', 
        'pie'
    ).order_by('id')
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ClientFilter
    ordering_fields = ['name', 'group', 'personal_number', 'sector_name', 'country_code', 'country_of_ubo_code']

    def _export_excel(self, queryset):
        columns = [
            'name',
            'group',
            'personal_number',
            'client_code',
            'bvd',
            'sector_name',
            'country_code',
            'country_of_ubo_code',
            'pie_name',
        ]

        headers = [
            'Name',
            'Group',
            'Personal Number',
            'Client Code',
            'BVD',
            'Sector',
            'Country',
            'Country of UBO',
            'Pie',
        ]

        return generate_excel(queryset, 'Clients', columns, headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        export_type = request.query_params.get('export')

        if export_type == 'excel':
            return self._export_excel(queryset)

        if request.query_params.get('all') == 'true':
            serializer = self.get_serializer(queryset, many=True)

            return Response(serializer.data)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_queryset(self):
        return Client.objects.annotate(
            sector_name=F('sector__name'),
            country_code=F('country__code'),
            country_of_ubo_code=F('country_of_ubo__code'),
            pie_name=F('pie__name'),
        )

    def paginate_queryset(self, queryset):
        

        return super().paginate_queryset(queryset)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            if self.action == 'retrieve':
                return ClientDetailSerializer

            return ClientSerializer

        return ClientCreateSerializer
