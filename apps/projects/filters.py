import django_filters

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(
        field_name='projectcode__code',
        lookup_expr='icontains'
    )
    is_code_recurring = django_filters.BooleanFilter(
        field_name='is_code_recurring'
    )
    status_name = django_filters.CharFilter(
        field_name='status__name',
        lookup_expr='icontains'
    )
    client_name = django_filters.CharFilter(
        field_name='client__name',
        lookup_expr='icontains'
    )
    manager_email = django_filters.CharFilter(
        field_name='manager__email',
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
    department_name = django_filters.CharFilter(
        field_name='department__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Project
        fields = []
