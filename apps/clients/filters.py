import django_filters

from .models import Client


class ClientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    group = django_filters.CharFilter(
        field_name='group',
        lookup_expr='icontains'
    )
    personal_number = django_filters.CharFilter(
        field_name='personal_number',
        lookup_expr='icontains'
    )
    sector_name = django_filters.CharFilter(
        field_name='sector__name',
        lookup_expr='icontains'
    )
    country_code = django_filters.CharFilter(
        field_name='country__code',
        lookup_expr='icontains'
    )
    country_of_ubo_code = django_filters.CharFilter(
        field_name='country_of_ubo__code',
        lookup_expr='icontains'
    )

    class Meta:
        model = Client
        fields = []
