import django_filters

from .models import User


class UserFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains'
    )
    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains'
    )
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains'
    )
    position_name = django_filters.CharFilter(
        field_name='position__name',
        lookup_expr='icontains'
    )
    department_name = django_filters.CharFilter(
        field_name='department__name',
        lookup_expr='icontains'
    )
    department_role_name = django_filters.CharFilter(
        field_name='department_role__name',
        lookup_expr='icontains'
    )
    grade_name = django_filters.CharFilter(
        field_name='grade__name',
        lookup_expr='icontains'
    )
    country_code = django_filters.CharFilter(
        field_name='country__code',
        lookup_expr='icontains'
    )
    role_name = django_filters.CharFilter(
        field_name='role__name',
        lookup_expr='icontains'
    )
    hired_after = django_filters.DateFilter(
        field_name='hired',
        lookup_expr='gte'
    )
    hired_before = django_filters.DateFilter(
        field_name='hired',
        lookup_expr='lte'
    )

    fired_after = django_filters.DateFilter(
        field_name='fired',
        lookup_expr='gte'
    )
    fired_before = django_filters.DateFilter(
        field_name='fired',
        lookup_expr='lte'
    )
    status_name = django_filters.CharFilter(
        field_name='status__name',
        lookup_expr='icontains'
    )

    class Meta:
        model = User
        fields = []
