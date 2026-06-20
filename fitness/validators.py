import re
from datetime import date
from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError

from .constants import MAX_MEMBERSHIP_PRICE, MIN_MEMBERSHIP_PRICE, PHONE_REGEX, ROLE_ADMIN


def validate_phone_format(phone: str) -> str:
    """
    Проверка формата контактного телефона.

    Args:
        phone: Телефон пользователя.
    """
    if not phone or not phone.strip():
        raise ValidationError('Укажите контактный телефон для записи на занятие.')
    normalized = re.sub(r'[\s\-()]', '', phone.strip())
    if not re.match(PHONE_REGEX, normalized):
        raise ValidationError(
            'Телефон должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX.'
        )
    return normalized


def validate_membership_price(price: Decimal | int | str) -> Decimal:
    """
    Проверка минимальной и максимальной стоимости абонемента.

    Args:
        price: Стоимость тарифа абонемента.
    """
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


def get_active_bookings_count(fitness_class: Any, exclude_booking_id: int | None = None) -> int:
    """
    Число занятых мест на занятии.

    Args:
        fitness_class: Объект занятия.
        exclude_booking_id: ID записи, которую нужно исключить из подсчёта.
    """
    qs = fitness_class.classbooking_set.filter(status__in=('booked', 'attended'))
    if exclude_booking_id:
        qs = qs.exclude(pk=exclude_booking_id)
    return qs.count()


def validate_class_capacity(fitness_class: Any, exclude_booking_id: int | None = None) -> None:
    """
    Проверка наличия свободных мест на занятии.

    Args:
        fitness_class: Объект занятия.
        exclude_booking_id: ID редактируемой записи.
    """
    occupied = get_active_bookings_count(fitness_class, exclude_booking_id)
    if occupied >= fitness_class.capacity:
        raise ValidationError(
            f'На занятие «{fitness_class.name}» нет свободных мест '
            f'({occupied}/{fitness_class.capacity}).'
        )


def validate_active_membership(user: Any, on_date: date | None = None) -> None:
    """
    Проверка активного абонемента у клиента.

    Args:
        user: Пользователь, который записывается на занятие.
        on_date: Дата, на которую проверяется активность абонемента.
    """
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


def user_can_access_booking(user: Any, booking: Any) -> bool:
    """
    Проверка прав доступа к записи.

    Args:
        user: Текущий пользователь.
        booking: Запись на занятие.
    """
    if not user:
        return False
    if getattr(user, 'role', None) and user.role.name == ROLE_ADMIN:
        return True
    return booking.user_id == user.id


def user_can_access_membership(user: Any, membership: Any) -> bool:
    """
    Проверка прав доступа к абонементу.

    Args:
        user: Текущий пользователь.
        membership: Абонемент.
    """
    if not user:
        return False
    if getattr(user, 'role', None) and user.role.name == ROLE_ADMIN:
        return True
    return membership.user_id == user.id
