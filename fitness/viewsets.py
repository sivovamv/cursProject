from datetime import date, datetime, timedelta

from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .authentication import get_fitness_user, is_administrator
from .filters import ClassBookingFilter, FitnessClassFilter, MembershipFilter
from .models import ClassBooking, FavoriteClass, FitnessClass, Membership, Trainer
from .permissions import IsAdministrator, IsOwnerOrAdministrator, ReadOnlyOrAdministrator
from .serializers import (
    ClassBookingSerializer,
    FavoriteClassSerializer,
    FitnessClassSerializer,
    MembershipSerializer,
    TrainerSerializer,
)


class FitnessClassViewSet(viewsets.ModelViewSet):
    serializer_class = FitnessClassSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FitnessClassFilter
    search_fields = ['name', 'trainer__user__full_name']
    ordering_fields = ['created_at', 'capacity', 'active_bookings_count', 'attended_count', 'favorite_count']
    ordering = ['-created_at']
    permission_classes = [ReadOnlyOrAdministrator]

    def get_queryset(self):
        queryset = FitnessClass.objects.select_related('trainer__user').annotate(
            active_bookings_count=Count(
                'classbooking',
                filter=Q(classbooking__status__in=('booked', 'attended')),
                distinct=True,
            ),
            attended_count=Count(
                'classbooking',
                filter=Q(classbooking__status='attended'),
                distinct=True,
            ),
            favorite_count=Count(
                'favoriteclass',
                distinct=True,
            ),
        )

        high_bookings = self.request.query_params.get('high_bookings')
        if high_bookings == 'true':
            queryset = queryset.filter(
                (Q(classbooking__status='booked') | Q(classbooking__status='attended')) &
                Q(capacity__gte=10) &
                ~Q(classbooking__status='canceled'),
            ).distinct()

        popular_recent = self.request.query_params.get('popular_recent')
        if popular_recent == 'true':
            week_ago = datetime.now() - timedelta(days=7)
            queryset = queryset.filter(
                (Q(classbooking__status='booked') | Q(capacity__gte=15)) &
                Q(created_at__gte=week_ago) &
                ~Q(created_at__lt=datetime.now() - timedelta(days=30)),
            ).distinct()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = get_fitness_user(self.request)
        if user:
            context['favorite_class_ids'] = set(
                FavoriteClass.objects.filter(user=user).values_list('fitness_class_id', flat=True)
            )
        else:
            context['favorite_class_ids'] = set()
        return context

    @action(methods=['GET'], detail=False)
    def popular_classes(self, request):
        classes = self.get_queryset().order_by('-active_bookings_count', '-favorite_count')[:10]
        serializer = self.get_serializer(classes, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAdministrator])
    def cancel_booking(self, request, pk=None):
        fitness_class = self.get_object()
        ClassBooking.objects.filter(
            fitness_class=fitness_class,
            status='booked',
        ).update(status='canceled')

        return Response({
            'status': 'success',
            'message': f'Все записи на занятие {fitness_class.name} отменены',
        }, status=status.HTTP_200_OK)


class ClassBookingViewSet(viewsets.ModelViewSet):
    serializer_class = ClassBookingSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClassBookingFilter
    search_fields = ['user__full_name', 'fitness_class__name']
    ordering_fields = ['created_at', 'start_time']
    ordering = ['-created_at']
    permission_classes = [IsOwnerOrAdministrator]

    def get_queryset(self):
        qs = ClassBooking.objects.select_related(
            'user',
            'user__role',
            'fitness_class',
            'fitness_class__trainer__user',
        )
        user = get_fitness_user(self.request)
        if user and not is_administrator(user):
            qs = qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        user = get_fitness_user(self.request)
        if user and not is_administrator(user):
            serializer.save(user=user)
        else:
            serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = get_fitness_user(request)
        if not is_administrator(user) and instance.user_id != getattr(user, 'id', None):
            raise PermissionDenied('Доступ к этой записи запрещён.')
        return super().retrieve(request, *args, **kwargs)


class FavoriteClassViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteClassSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['fitness_class', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [IsOwnerOrAdministrator]

    def get_queryset(self):
        qs = FavoriteClass.objects.select_related('user', 'user__role', 'fitness_class', 'fitness_class__trainer__user')
        user = get_fitness_user(self.request)
        if user and not is_administrator(user):
            qs = qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        user = get_fitness_user(self.request)
        if user and not is_administrator(user):
            serializer.save(user=user)
        else:
            serializer.save()


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MembershipFilter
    search_fields = ['user__full_name', 'tariff_type__name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    permission_classes = [IsOwnerOrAdministrator]

    def get_queryset(self):
        queryset = Membership.objects.select_related('user', 'user__role', 'tariff_type')
        user = get_fitness_user(self.request)
        if user and not is_administrator(user):
            queryset = queryset.filter(user=user)

        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            today = date.today()
            week_later = today + timedelta(days=7)
            year_start = date(today.year, 1, 1)
            queryset = queryset.filter(
                (Q(status='active') | Q(end_date__gte=today, end_date__lte=week_later)) &
                Q(start_date__gte=year_start) &
                ~Q(status='frozen'),
            )

        urgent_memberships = self.request.query_params.get('urgent')
        if urgent_memberships == 'true':
            today = date.today()
            queryset = queryset.filter(
                (Q(status='active') | Q(end_date__gte=today, end_date__lte=today + timedelta(days=3))) &
                Q(created_by__isnull=False) &
                ~Q(end_date__lt=today),
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = get_fitness_user(request)
        if not is_administrator(user) and instance.user_id != getattr(user, 'id', None):
            raise PermissionDenied('Доступ к этому абонементу запрещён.')
        return super().retrieve(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def active_memberships(self, request):
        active = self.get_queryset().filter(
            status='active',
            start_date__lte=date.today(),
            end_date__gte=date.today(),
        )
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def freeze_membership(self, request, pk=None):
        membership = self.get_object()
        if membership.status == 'active':
            membership.status = 'frozen'
            membership.save()
            return Response({
                'status': 'success',
                'message': 'Абонемент заморожен',
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Можно заморозить только активный абонемент',
        }, status=status.HTTP_400_BAD_REQUEST)


class TrainerViewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.select_related('user').all()
    serializer_class = TrainerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['specialization']
    search_fields = ['user__full_name', 'specialization']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [ReadOnlyOrAdministrator]

    @action(methods=['POST'], detail=True, permission_classes=[IsAdministrator])
    def update_specialization(self, request, pk=None):
        trainer = self.get_object()
        new_specialization = request.data.get('specialization')

        if not new_specialization:
            return Response({
                'error': 'Поле specialization обязательно',
            }, status=status.HTTP_400_BAD_REQUEST)

        trainer.specialization = new_specialization
        trainer.save()

        serializer = self.get_serializer(trainer)
        return Response(serializer.data)
