import re
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

from .constants import MAX_MEMBERSHIP_PRICE, MIN_MEMBERSHIP_PRICE, PHONE_REGEX, ROLE_ADMIN


def validate_phone_format(phone):
    """Проверка формата контактного телефона (+7 или 8 и 10 цифр)."""
    if not phone or not phone.strip():
        raise ValidationError('Укажите контактный телефон для записи на занятие.')
    normalized = re.sub(r'[\s\-()]', '', phone.strip())
    if not re.match(PHONE_REGEX, normalized):
        raise ValidationError(
            'Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX.'
        )
    return normalized


def validate_membership_price(price):
    """Проверка минимальной и максимальной стоимости абонемента."""
    price = Decimal(str(price))
    if price < MIN_MEMBERSHIP_PRICE:
        raise ValidationError(
            f'Минимальная стоимость абонемента — {MIN_MEMBERSHIP_PRICE} руб.'
        )
    if price > MAX_MEMBERSHIP_PRICE:
        raise ValidationError(
            f'Максимальная стоимость абонемента — {MAX_MEMBERSHIP_PRICE:,} руб.'.replace(',', ' ')
        )
    return price


def get_active_bookings_count(fitness_class, exclude_booking_id=None):
    """Число занятых мест на занятии (статусы booked и attended)."""
    qs = fitness_class.classbooking_set.filter(status__in=('booked', 'attended'))
    if exclude_booking_id:
        qs = qs.exclude(pk=exclude_booking_id)
    return qs.count()


def validate_class_capacity(fitness_class, exclude_booking_id=None):
    """Проверка наличия свободных мест на занятии."""
    occupied = get_active_bookings_count(fitness_class, exclude_booking_id)
    if occupied >= fitness_class.capacity:
        raise ValidationError(
            f'На занятие «{fitness_class.name}» нет свободных мест '
            f'({occupied}/{fitness_class.capacity}).'
        )


def validate_active_membership(user, on_date=None):
    """Проверка активного абонемента у клиента."""
    on_date = on_date or date.today()
    has_membership = user.memberships.filter(
        status='active',
        start_date__lte=on_date,
        end_date__gte=on_date,
    ).exists()
    if not has_membership:
        raise ValidationError(
            'Для записи на занятие необходим активный абонемент.'
        )


def user_can_access_booking(user, booking):
    """Проверка прав доступа к записи: владелец или администратор."""
    if not user:
        return False
    if getattr(user, 'role', None) and user.role.name == ROLE_ADMIN:
        return True
    return booking.user_id == user.id


def user_can_access_membership(user, membership):
    """Проверка прав доступа к абонементу: владелец или администратор."""
    if not user:
        return False
    if getattr(user, 'role', None) and user.role.name == ROLE_ADMIN:
        return True
    return membership.user_id == user.id
