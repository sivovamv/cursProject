import django_filters
from django.db.models import F

from .models import ClassBooking, FitnessClass, Membership


class FitnessClassFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    trainer_name = django_filters.CharFilter(field_name='trainer__user__full_name', lookup_expr='icontains')
    capacity_min = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    capacity_max = django_filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    has_free_spots = django_filters.BooleanFilter(method='filter_has_free_spots')

    class Meta:
        model = FitnessClass
        fields = ('trainer', 'name', 'trainer_name', 'capacity_min', 'capacity_max', 'has_free_spots')

    def filter_has_free_spots(self, queryset, name, value):
        if value:
            return queryset.filter(capacity__gt=F('active_bookings_count'))
        return queryset.filter(capacity__lte=F('active_bookings_count'))


class MembershipFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='tariff_type__price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='tariff_type__price', lookup_expr='lte')
    start_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Membership
        fields = ('status', 'tariff_type', 'user', 'price_min', 'price_max', 'start_after', 'end_before')


class ClassBookingFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')
    class_name = django_filters.CharFilter(field_name='fitness_class__name', lookup_expr='icontains')

    class Meta:
        model = ClassBooking
        fields = (
            'status',
            'fitness_class',
            'user',
            'class_name',
            'created_after',
            'created_before',
        )
