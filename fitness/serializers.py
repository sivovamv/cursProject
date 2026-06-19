from rest_framework import serializers

from .models import ClassBooking, FitnessClass, Membership, Trainer, User
from .validators import (
    get_active_bookings_count,
    validate_active_membership,
    validate_class_capacity,
    validate_membership_price,
    validate_phone_format,
)


class FitnessClassSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.user.full_name', read_only=True)
    bookings_count = serializers.SerializerMethodField()
    free_spots = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        fields = (
            'id', 'name', 'description', 'trainer', 'trainer_name',
            'capacity', 'bookings_count', 'free_spots', 'created_at',
        )
        read_only_fields = ('created_at',)

    def get_bookings_count(self, obj):
        if hasattr(obj, 'active_bookings_count'):
            return obj.active_bookings_count
        return get_active_bookings_count(obj)

    def get_free_spots(self, obj):
        occupied = self.get_bookings_count(obj)
        return max(obj.capacity - occupied, 0)

    def validate_capacity(self, value):
        if value < 1 or value > 50:
            raise serializers.ValidationError('Вместимость должна быть от 1 до 50 человек')
        return value


class MembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    tariff_type_name = serializers.CharField(source='tariff_type.name', read_only=True)
    tariff_price = serializers.DecimalField(
        source='tariff_type.price', max_digits=10, decimal_places=2, read_only=True,
    )
    visits_count = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = (
            'id', 'user', 'user_name', 'tariff_type', 'tariff_type_name', 'tariff_price',
            'start_date', 'end_date', 'status', 'visits_count', 'created_at',
        )
        read_only_fields = ('created_at',)

    def get_visits_count(self, obj):
        from datetime import date
        return ClassBooking.objects.filter(
            user=obj.user,
            status='attended',
            start_time__isnull=False,
            start_time__date__gte=obj.start_date,
            start_time__date__lte=obj.end_date,
        ).count()

    def validate(self, data):
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'Дата окончания должна быть позже даты начала',
            })

        tariff_type = data.get('tariff_type', getattr(self.instance, 'tariff_type', None))
        if tariff_type:
            try:
                validate_membership_price(tariff_type.price)
            except Exception as exc:
                raise serializers.ValidationError({'tariff_type': exc.messages})

        return data


class TrainerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    classes_count = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = ('id', 'user', 'user_name', 'specialization', 'classes_count', 'created_at')
        read_only_fields = ('created_at',)

    def get_classes_count(self, obj):
        return obj.fitnessclass_set.count()

    def validate_specialization(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError('Специализация должна содержать минимум 2 символа')
        return value.strip()


class ClassBookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)

    class Meta:
        model = ClassBooking
        fields = (
            'id', 'user', 'user_name', 'fitness_class', 'class_name',
            'status', 'start_time', 'end_time', 'created_at',
        )
        read_only_fields = ('created_at',)

    def validate(self, data):
        user = data.get('user', getattr(self.instance, 'user', None))
        fitness_class = data.get('fitness_class', getattr(self.instance, 'fitness_class', None))
        status = data.get('status', getattr(self.instance, 'status', 'booked'))

        if status in ('booked', 'attended') and user and fitness_class:
            try:
                validate_phone_format(user.phone)
            except Exception as exc:
                raise serializers.ValidationError({'user': exc.messages})

            try:
                validate_active_membership(user)
            except Exception as exc:
                raise serializers.ValidationError({'user': exc.messages})

            try:
                validate_class_capacity(
                    fitness_class,
                    exclude_booking_id=getattr(self.instance, 'pk', None),
                )
            except Exception as exc:
                raise serializers.ValidationError({'fitness_class': exc.messages})

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'phone', 'birth_date', 'role_name')
        read_only_fields = ('role_name',)

    def validate_phone(self, value):
        if value:
            try:
                return validate_phone_format(value)
            except Exception as exc:
                raise serializers.ValidationError(exc.messages)
        return value
